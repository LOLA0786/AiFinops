from __future__ import annotations
import os
import json
import subprocess
import time
from typing import List, Dict, Any, Optional

try:
    import pynvml  # type: ignore
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False

from .llm_clients import LLMClient
from .terminate_workflow import stop_instances_safe, post_approval_request
from .inventory import fetch_ec2_inventory

CONFIRM = os.getenv("CONFIRM_GPU_ACTIONS", "false").lower() in ("1","true","yes")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

def _run_nvidia_smi_query() -> List[Dict[str, Any]]:
    """Query using nvidia-smi CLI (safer fallback)."""
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=index,name,utilization.gpu,utilization.memory,memory.total,memory.used",
            "--format=csv,noheader,nounits"
        ], stderr=subprocess.DEVNULL).decode().strip()
        rows = []
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 6:
                continue
            idx, name, util, mem_util, mem_total, mem_used = parts[:6]
            rows.append({
                "index": int(idx),
                "name": name,
                "gpu_util": float(util),
                "mem_util": float(mem_util),
                "mem_total": float(mem_total),
                "mem_used": float(mem_used),
            })
        return rows
    except Exception:
        return []

def collect_gpu_metrics_local() -> List[Dict[str, Any]]:
    """Return list of GPUs with metrics using NVML if available otherwise nvidia-smi fallback."""
    if NVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            res = []
            for i in range(device_count):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(h).decode()
                util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(h)
                mem_total = mem_info.total / (1024**2)
                mem_used = mem_info.used / (1024**2)
                mem_util = (mem_used / mem_total * 100) if mem_total else 0.0
                res.append({
                    "index": i,
                    "name": name,
                    "gpu_util": float(util),
                    "mem_util": float(mem_util),
                    "mem_total": mem_total,
                    "mem_used": mem_used
                })
            pynvml.nvmlShutdown()
            return res
        except Exception:
            return _run_nvidia_smi_query()
    else:
        return _run_nvidia_smi_query()

def detect_gpu_issues(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect common issues per GPU."""
    out = []
    for s in samples:
        issues = []
        if s.get("gpu_util", 0) < 10:
            issues.append("gpu_idle")
        if s.get("mem_used", 0) > 0 and s.get("gpu_util", 0) < 20:
            issues.append("mem_high_compute_low")
        if s.get("mem_used", 0) == 0 and s.get("gpu_util", 0) == 0:
            issues.append("zombie_gpu")
        out.append({"gpu_index": s.get("index"), "name": s.get("name"), "metrics": s, "issues": issues})
    return out

def estimate_waste_cost(hours: float, gpu_price_per_hour: float = 36.0) -> float:
    """Estimate waste cost (H100-like pricing default)."""
    return hours * gpu_price_per_hour

async def explain_with_llm(issues: List[Dict[str, Any]], context: Optional[str] = None) -> str:
    """
    Use LLM to explain the issues and recommend fixes.
    Returns a textual explanation.
    """
    client = LLMClient(provider=LLM_PROVIDER)
    prompt_lines = ["You are an expert GPU FinOps assistant. For each GPU issue below, explain cause and recommend fixes."]
    if context:
        prompt_lines.append("Context: " + context)
    for i, it in enumerate(issues):
        prompt_lines.append(f"GPU {i}: {it['name']} - metrics: {it['metrics']} - issues: {it['issues']}")
    user_prompt = "\\n".join(prompt_lines)
    # system prompt to be concise and actionable
    system = "Be concise. Provide 1-2 actionable fixes per issue and a suggested Terraform/Helm change if applicable."
    try:
        text = await client.chat(user_prompt, system=system)
    except Exception as e:
        text = "LLM explanation failed: " + str(e)
    return text

def find_ec2_gpu_instances(region: str = "us-east-1") -> List[Dict[str, Any]]:
    """Map EC2 inventory to GPU instances (heuristic: instance type names containing p|g)."""
    insts = fetch_ec2_inventory(region=region)
    gpu_insts = []
    for i in insts:
        t = i.get("InstanceType","").lower()
        if any(x in t for x in ("p4","p5","g4","g5","p3","a100","h100","p4d")):
            gpu_insts.append(i)
    return gpu_insts

def request_stop_for_instances(instance_ids: List[str], reason: str, region: str = "us-east-1") -> Dict[str, Any]:
    """
    Safe flow to stop instances:
    - prepare Slack approval (post_approval_request)
    - stop_instances_safe called only after explicit approval
    """
    req_id = ("gpu-stop-" + str(int(time.time())))
    post_approval_request([{"InstanceId": iid} for iid in instance_ids], request_id=req_id)
    return {"status": "approval_requested", "request_id": req_id, "instances": instance_ids, "reason": reason}

def auto_action_stop_idle_local(dry_run: bool = True, region: str = "us-east-1") -> Dict[str, Any]:
    """
    Detect local GPU idles and propose action on EC2 mapping if found.
    dry_run True -> return plan. dry_run False requires CONFIRM and will call stop_instances_safe.
    """
    metrics = collect_gpu_metrics_local()
    issues = detect_gpu_issues(metrics)
    # map to ec2 instances heuristically
    ec2_candidates = find_ec2_gpu_instances(region=region)
    candidate_ids = [c["InstanceId"] for c in ec2_candidates][:3]
    plan = {"metrics": metrics, "issues": issues, "candidate_ec2_instances": candidate_ids}
    if dry_run:
        return {"status": "dry_run", "plan": plan}
    if not CONFIRM:
        raise PermissionError("GPU auto-actions disabled. Set CONFIRM_GPU_ACTIONS=true to permit.")
    return stop_instances_safe(candidate_ids, dry_run=False, region=region)
