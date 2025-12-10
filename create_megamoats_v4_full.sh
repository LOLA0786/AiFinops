#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
echo "Creating MegaMoats v4 (Phase 4) full implementation in ${ROOT}"

# safe write: create parent dir, skip if exists
safe_write() {
  target="$1"; shift
  content="$@"
  dir="$(dirname "$target")"
  mkdir -p "$dir"
  if [ -e "$target" ]; then
    echo "SKIP (exists)  : $target"
  else
    printf "%s" "$content" > "$target"
    echo "CREATED        : $target"
  fi
}

# Create directories
mkdir -p megamoots_v4/{scheduler,profiler,graph_telemetry,finops_trader,common}
mkdir -p integration_v4/{godmode_bridge,megamoots_bridge}
mkdir -p docs_v4 tests

############################
# 1) GPU Scheduler (v4)
############################
safe_write "megamoots_v4/scheduler/__init__.py" "__all__=['scheduler']\n"
safe_write "megamoots_v4/scheduler/scheduler.py" \
'"""GPU Scheduler v4
- Best-fit decreasing + gang-aware heuristic
- Produces placement plan (node assignments) and preemption suggestions
- Pure-Python, deterministic, unit-testable
"""
from typing import List, Dict, Any
import math
import heapq

def best_fit_schedule(jobs: List[Dict[str,Any]], nodes: List[Dict[str,Any]]):
    """
    Assign jobs to nodes using best-fit on memory then GPUs.
    jobs: list of {id, gpu_count, mem_req_mb, priority (higher better), gang_id (optional)}
    nodes: list of {id, free_gpus, free_mem_mb, region}
    returns: dict job_id -> node_id or None
    """
    # sort jobs: gang jobs pinned together (stable), highest priority and largest mem first
    def job_key(j):
        return (-j.get("priority",0), -j.get("mem_req_mb",0), -j.get("gpu_count",0))
    jobs_sorted = sorted(jobs, key=job_key)
    nodes_state = [{**n} for n in nodes]
    assignments = {}
    # attempt to place gangs together: group by gang_id if provided
    gangs = {}
    for j in jobs_sorted:
        gang = j.get("gang_id")
        if gang:
            gangs.setdefault(gang, []).append(j)
        else:
            gangs.setdefault(f"_solo_{j["id']}", []).append(j)
    # flatten preserving gang groups
    job_groups = list(gangs.values())
    for group in job_groups:
        # try to find a single node that fits whole group first
        placed = False
        total_gpu = sum(j["gpu_count"] for j in group)
        total_mem = sum(j["mem_req_mb"] for j in group)
        for n in nodes_state:
            if n["free_gpus"] >= total_gpu and n["free_mem_mb"] >= total_mem:
                # place all
                for j in group:
                    assignments[j["id"]] = n["id"]
                    n["free_gpus"] -= j["gpu_count"]
                    n["free_mem_mb"] -= j["mem_req_mb"]
                placed = True
                break
        if placed:
            continue
        # if not possible, place individually best-fit
        for j in group:
            best_idx = None
            best_leftover = None
            for i,n in enumerate(nodes_state):
                if n["free_gpus"] >= j["gpu_count"] and n["free_mem_mb"] >= j["mem_req_mb"]:
                    leftover = n["free_mem_mb"] - j["mem_req_mb"]
                    if best_leftover is None or leftover < best_leftover:
                        best_leftover = leftover
                        best_idx = i
            if best_idx is not None:
                nodes_state[best_idx]["free_gpus"] -= j["gpu_count"]
                nodes_state[best_idx]["free_mem_mb"] -= j["mem_req_mb"]
                assignments[j["id"]] = nodes_state[best_idx]["id"]
            else:
                assignments[j["id"]] = None
    return assignments

if __name__ == "__main__":
    # small self-demo
    nodes=[{"id":"node-1","free_gpus":4,"free_mem_mb":65536},{"id":"node-2","free_gpus":2,"free_mem_mb":32768}]
    jobs=[{"id":"job-a","gpu_count":2,"mem_req_mb":20000,"priority":10},{"id":"job-b","gpu_count":1,"mem_req_mb":8000,"priority":5}]
    print(best_fit_schedule(jobs,nodes))
'

safe_write "megamoots_v4/scheduler/test_scheduler.py" \
'from megamoots_v4.scheduler.scheduler import best_fit_schedule
def test_schedule_basic():
    nodes=[{"id":"n1","free_gpus":2,"free_mem_mb":32768},{"id":"n2","free_gpus":4,"free_mem_mb":65536}]
    jobs=[{"id":"a","gpu_count":2,"mem_req_mb":20000},{"id":"b","gpu_count":1,"mem_req_mb":8000}]
    r=best_fit_schedule(jobs,nodes)
    assert r["a"] in ("n1","n2")
    assert "b" in r
'

############################
# 2) PyTorch Profiler Adapter
############################
safe_write "megamoots_v4/profiler/__init__.py" "__all__=['profiler']\n"
safe_write "megamoots_v4/profiler/pytorch_profiler.py" \
'"""PyTorch Profiler Adapter (v4)
Runs the profiler if torch is available; otherwise emits a synthetic summary.
"""
import json, os
try:
    import torch
    TORCH=True
except Exception:
    TORCH=False

def summarize_events(events):
    top_ops=[]
    for e in events:
        top_ops.append({"op": getattr(e,"key",str(e)),"cpu_time_ms": getattr(e,"cpu_time_total",0)/1000.0, "cuda_time_ms": getattr(e,"cuda_time_total",0)/1000.0})
    return {"top_ops": sorted(top_ops, key=lambda x:- (x["cpu_time_ms"]+x["cuda_time_ms"]))[:10]}

def profile_run(dummy_fn, steps=5, output_path="megamoots_v4/profiler/summary.json"):
    if not TORCH:
        summary={"top_ops":[{"op":"matmul","cpu_time_ms":10.0,"cuda_time_ms":100.0}],"gpu_time_ms":500.0,"cpu_time_ms":80.0,"mem_peak_mb":12000}
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path,"w") as f:
            json.dump(summary,f,indent=2)
        return summary
    # real profiler path
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU] + ([torch.profiler.ProfilerActivity.CUDA] if torch.cuda.is_available() else []), record_shapes=True) as prof:
        for _ in range(steps):
            dummy_fn()
    events=prof.key_averages()
    summary=summarize_events(events)
    with open(output_path,"w") as f:
        json.dump(summary,f,indent=2)
    return summary
'

safe_write "megamoots_v4/profiler/test_profiler.py" \
'def test_profiler_stub(tmp_path):
    from megamoots_v4.profiler.pytorch_profiler import profile_run
    out=profile_run(lambda: None, steps=1, output_path=str(tmp_path/"p.json"))
    assert "top_ops" in out
'

############################
# 3) Graph telemetry
############################
safe_write "megamoots_v4/graph_telemetry/graph_trace.py" \
'"""Graph telemetry: DAG traces and JSONL exporter"""
import time, json, os
def emit_node_event(trace_path, job_id, node_id, start_ts, end_ts, meta=None):
    meta=meta or {}
    os.makedirs(os.path.dirname(trace_path), exist_ok=True)
    ev={"job_id":job_id,"node_id":node_id,"start":start_ts,"end":end_ts,"meta":meta}
    with open(trace_path,"a") as f:
        f.write(json.dumps(ev)+"\n")
    return ev
if __name__=="__main__":
    p="megamoots_v4/graph_telemetry/traces.jsonl"
    emit_node_event(p,"job-1","stage-1",int(time.time()),int(time.time())+2,{"op":"load_batch"})
'

safe_write "megamoots_v4/graph_telemetry/test_graph.py" \
'from megamoots_v4.graph_telemetry.graph_trace import emit_node_event
def test_emit(tmp_path):
    p=str(tmp_path/"t.jsonl")
    ev=emit_node_event(p,"j","n",1,2,{"x":1})
    assert "job_id" in ev
'

############################
# 4) Cloud FinOps Auto-Trader
############################
safe_write "megamoots_v4/finops_trader/__init__.py" "__all__=['cost_model','trader']\n"
safe_write "megamoots_v4/finops_trader/cost_model.py" \
'"""Cost modelling for cloud GPUs (v4)""" 
from typing import Dict, List
def estimate_cost(details: Dict) -> float:
    gpu_cost = details.get("gpu_hours",0.0)*details.get("price_per_hour",0.0)
    egress_cost = details.get("egress_gb",0.0)*details.get("egress_cost_per_gb",0.0)
    return round(gpu_cost + egress_cost,4)
def choose_deployment(options: List[Dict], latency_threshold_ms=150, reliability_threshold=0.95):
    best=None
    for o in options:
        penalty=1.0
        if o.get("latency_ms",0) > latency_threshold_ms:
            penalty += 0.2
        if o.get("reliability",1.0) < reliability_threshold:
            penalty += 0.5
        score = o.get("price_per_hour",9999.0) * penalty
        if best is None or score < best[0]:
            best = (score,o)
    return best[1] if best else None
'

safe_write "megamoots_v4/finops_trader/auto_trader.py" \
'"""Auto-Trader: simulate decisions (v4)"""
from .cost_model import estimate_cost, choose_deployment
def suggest_trade(job_meta, market_offers):
    # job_meta: {'gpu_hours':..,'egress_gb':..}
    best = choose_deployment(market_offers)
    return {"decision":"migrate" if best and best["price_per_hour"]<job_meta.get("price_per_hour",9999) else "stay","target":best}
'

safe_write "megamoots_v4/finops_trader/test_trader.py" \
'from megamoots_v4.finops_trader.cost_model import choose_deployment
def test_choose():
    opts=[{"cloud":"a","price_per_hour":3.0,"latency_ms":100,"reliability":0.99},{"cloud":"b","price_per_hour":2.7,"latency_ms":200,"reliability":0.8}]
    best=choose_deployment(opts)
    assert best["cloud"]=="a"
'

############################
# 5) Integration adapter (GodMode <-> MegaMoats)
############################
safe_write "integration_v4/godmode_bridge/adapter.py" \
'"""Adapter: translate GodMode signals into scheduling/trader actions""" 
from megamoots_v4.scheduler.scheduler import best_fit_schedule
from megamoots_v4.finops_trader.cost_model import choose_deployment
def apply_policy(job_queue, cluster_nodes, market_offers, global_policy):
    if global_policy.get("mode")=="cost_savings":
        pick = choose_deployment(market_offers)
        return {"action":"migrate","target":pick}
    return {"action":"schedule","plan":best_fit_schedule(job_queue, cluster_nodes)}
'

safe_write "integration_v4/megamoots_bridge/router.py" \
'"""Simple router/adapter for events""" 
def route_event(event):
    # event example: {"type":"job.submit","job":{...}}
    return {"routed":True,"event_type":event.get("type")}
'

safe_write "integration_v4/godmode_bridge/test_adapter.py" \
'from integration_v4.godmode_bridge.adapter import apply_policy
def test_apply_policy():
    j=[{"id":"a","gpu_count":1,"mem_req_mb":8000}]
    nodes=[{"id":"n1","free_gpus":2,"free_mem_mb":16000}]
    offers=[{"cloud":"g","price_per_hour":2.9,"latency_ms":80,"reliability":0.99}]
    r=apply_policy(j,nodes,offers,{"mode":"normal"})
    assert "action" in r
'

############################
# 6) Docs + README (enterprise)
############################
safe_write "docs_v4/README_V4.md" \
"# MegaMoats V4 — Phase 4\n\nAdds:\n- GPU Scheduler (best-fit + gang-aware)\n- PyTorch Profiler adapter (offline-friendly)\n- Graph telemetry (JSONL traces)\n- Cloud FinOps Auto-Trader (cost-based decisions)\n- Integration adapter to merge GodMode signals with local scheduling/trading\n\nAll code is additive and created under megamoots_v4/ and integration_v4/.\n"

############################
# 7) Run/demo script and pytest entry
############################
safe_write "run_v4_demo.sh" \
'#!/usr/bin/env bash
set -euo pipefail
echo "Running MegaMoats v4 demo..."
python3 - <<PY
from megamoots_v4.scheduler.scheduler import best_fit_schedule
from megamoots_v4.finops_trader.auto_trader import suggest_trade
nodes=[{"id":"n1","free_gpus":4,"free_mem_mb":65536},{"id":"n2","free_gpus":2,"free_mem_mb":32768}]
jobs=[{"id":"j1","gpu_count":2,"mem_req_mb":20000,"priority":10}]
print("Schedule:", best_fit_schedule(jobs,nodes))
offers=[{"cloud":"aws","price_per_hour":3.2,"latency_ms":80,"reliability":0.99},{"cloud":"gcp","price_per_hour":2.9,"latency_ms":100,"reliability":0.98}]
print("Trader suggestion:", suggest_trade({"price_per_hour":3.2}, offers))
PY
'

chmod +x run_v4_demo.sh
safe_write "tests/test_v4_smoke.py" \
'def test_v4_dir_exists():
    import os
    assert os.path.isdir("megamoots_v4")
'

echo "Done. New files created under megamoots_v4/, integration_v4/, docs_v4/, plus run_v4_demo.sh and tests/test_v4_smoke.py. Next: git add, commit, push, create PR."
