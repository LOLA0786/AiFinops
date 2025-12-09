from __future__ import annotations
import re
from typing import List, Dict, Optional

# Simple log parsers for common frameworks (PyTorch/HuggingFace)
LOSS_LINE = re.compile(r"(loss[:=]\s*[0-9\.eE+-]+)", re.IGNORECASE)
GPU_UTIL_LINE = re.compile(r"(gpu.*util|gpu.*usage|gpu_util)[^\n]*([0-9]{1,3})", re.IGNORECASE)
CUDA_ERROR = re.compile(r"(cuda|out of memory|oom|CUDA error)", re.IGNORECASE)
DATALOADER_LINE = re.compile(r"(dataloader|num_workers|DataLoader)", re.IGNORECASE)

def parse_training_log(text: str, max_lines: int = 200) -> Dict:
    """
    Returns structured summary from training logs (very lightweight).
    """
    lines = text.strip().splitlines()[-max_lines:]
    summary = {"loss_trend": None, "errors": [], "gpu_suspicious": [], "dataloader_lines": []}
    losses = []
    for ln in lines:
        m = LOSS_LINE.search(ln)
        if m:
            try:
                val = float(re.findall(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", m.group(1))[0])
                losses.append(val)
            except Exception:
                pass
        if CUDA_ERROR.search(ln):
            summary["errors"].append(ln.strip())
        if GPU_UTIL_LINE.search(ln):
            summary["gpu_suspicious"].append(ln.strip())
        if DATALOADER_LINE.search(ln):
            summary["dataloader_lines"].append(ln.strip())
    if losses:
        summary["loss_trend"] = {"first": losses[0], "last": losses[-1], "count": len(losses)}
    return summary

# LLM prompt templates to diagnose issues (you pass parse result + metrics)
LLM_PROMPT_TEMPLATE = \"\"\"You are a pragmatic ML engineer diagnosing training problems.

Context:
{context}

Observed summary:
{summary}

Provide:
1) A concise diagnosis (1-2 lines).
2) Top 3 prioritized fixes (code example where possible).
3) Suggested trainer/loader arg changes (num_workers, batch_size, prefetch_factor).
4) If applicable, a single-line Terraform/Helm change (example) to reduce GPU allocation.

Be short and actionable.
\"\"\"

def build_llm_prompt(context: str, summary: Dict) -> str:
    return LLM_PROMPT_TEMPLATE.format(context=context, summary=summary)
