#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
mkdir -p megamoots_v5/recommender megamoots_v5/cost_preview megamoots_v5/sharing megamoots_v5/carbon demo_v5 docs_v5

# 1) GPU Recommender scaffold
cat > megamoots_v5/recommender/recommender.py <<'PY'
"""
GPU Recommender
Inputs: job_profile dict {model_params, batch_size, dataset_size, training_hours_estimate}
Output: recommendation dict {gpu_type, est_runtime_hours, est_cost_usd, notes}
Simple rule-based heuristics with pluggable cost model.
"""
from typing import Dict, Any, Tuple

# Example GPU catalog (USD/hr on-demand - replace with actual oracle)
GPU_CATALOG = {
    "A10G": {"mem_gb": 24, "perf_score": 1.0, "usd_hr": 0.8},
    "A100": {"mem_gb": 40, "perf_score": 3.5, "usd_hr": 3.5},
    "H100": {"mem_gb": 80, "perf_score": 6.5, "usd_hr": 7.0},
}

def estimate_runtime(job_profile: Dict[str,Any], gpu_perf: float) -> float:
    # naive: runtime scales inversely with perf_score, and linearly with work_units
    work = job_profile.get("work_units", 1.0)
    base_hours = job_profile.get("base_hours", 1.0)
    runtime = base_hours * work / gpu_perf
    return max(0.1, runtime)

def recommend(job_profile: Dict[str,Any]) -> Dict[str,Any]:
    results = []
    for name, specs in GPU_CATALOG.items():
        perf = specs["perf_score"]
        est_hours = estimate_runtime(job_profile, perf)
        est_cost = est_hours * specs["usd_hr"]
        mem_ok = specs["mem_gb"] >= job_profile.get("mem_required_gb", 8)
        results.append({
            "gpu": name,
            "mem_gb": specs["mem_gb"],
            "est_hours": round(est_hours,2),
            "est_cost_usd": round(est_cost,2),
            "mem_sufficient": mem_ok
        })
    # choose cheapest that satisfies memory, otherwise highest perf
    mem_satisfiers = [r for r in results if r["mem_sufficient"]]
    if mem_satisfiers:
        choice = min(mem_satisfiers, key=lambda r: r["est_cost_usd"])
    else:
        choice = max(results, key=lambda r: r["mem_gb"])
    return {"input": job_profile, "candidates": results, "choice": choice}

if __name__ == "__main__":
    sample = {"work_units": 10, "base_hours": 2.5, "mem_required_gb": 32}
    import json
    print(json.dumps(recommend(sample), indent=2))
PY

# 2) Training Job Cost Preview scaffold
cat > megamoots_v5/cost_preview/cost_preview.py <<'PY'
"""
Training Job Cost Preview
Given a job spec, provide cost and runtime estimates for spot vs on-demand and simple recommendations.
"""
from typing import Dict, Any

# Simple price map - replace with dynamic oracle later
PRICE = {
    "A100": {"on_demand": 3.5, "spot": 1.2},
    "H100": {"on_demand": 7.0, "spot": 2.4},
}

def cost_preview(job_spec: Dict[str,Any]) -> Dict[str,Any]:
    # job_spec: {gpu_type, gpus, est_hours_per_gpu, checkpoint_overhead_pct}
    gpu = job_spec.get("gpu_type","A100")
    gpus = job_spec.get("gpus",1)
    hours = job_spec.get("est_hours_per_gpu",1.0)
    chk_pct = job_spec.get("checkpoint_overhead_pct", 0.05)
    on_demand = PRICE.get(gpu, PRICE["A100"])["on_demand"]
    spot = PRICE.get(gpu, PRICE["A100"])["spot"]
    cost_on = on_demand * gpus * hours * (1+chk_pct)
    cost_spot = spot * gpus * hours * (1+chk_pct)
    recommendation = "spot+checkpointing" if cost_spot < cost_on * 0.8 else "on-demand"
    return {
        "job_spec": job_spec,
        "cost_on_demand_usd": round(cost_on,2),
        "cost_spot_usd": round(cost_spot,2),
        "recommended": recommendation
    }

if __name__ == "__main__":
    demo = {"gpu_type":"A100","gpus":8,"est_hours_per_gpu":14,"checkpoint_overhead_pct":0.03}
    import json
    print(json.dumps(cost_preview(demo), indent=2))
PY

# 3) GPU Sharing Intelligence scaffold (MIG/MPS suggestion)
cat > megamoots_v5/sharing/sharing_optimizer.py <<'PY'
"""
GPU Sharing Intelligence
Simple heuristics to propose MIG splits or time-sharing if utilization low.
Input: list of pods with memory/peak usage, GPU capacity
"""
from typing import List, Dict, Any

def suggest_sharing(pods: List[Dict[str,Any]], gpu_capacity_gb:int=80) -> Dict[str,Any]:
    # pods: [{'name':str, 'mem_gb':int, 'avg_util_pct':int}]
    total_mem = sum(p['mem_gb'] for p in pods)
    avg_util = sum(p['avg_util_pct'] for p in pods)/max(1,len(pods))
    suggestion = {}
    if total_mem < gpu_capacity_gb and avg_util < 40:
        suggestion['strategy'] = "MIG_split or colocate"
        suggestion['message'] = f"Total mem {total_mem}GB < {gpu_capacity_gb}GB and avg util {avg_util:.1f}% → safe to share"
    elif avg_util < 60:
        suggestion['strategy'] = "Time-slicing/MPS"
        suggestion['message'] = "Consider MPS or time-slicing for latency-tolerant workloads"
    else:
        suggestion['strategy'] = "No_sharing"
        suggestion['message'] = "High utilization — do NOT share"
    suggestion['pods'] = pods
    return suggestion

if __name__ == "__main__":
    pods = [{"name":"train-A","mem_gb":20,"avg_util_pct":25},{"name":"infer-B","mem_gb":12,"avg_util_pct":15}]
    import json
    print(json.dumps(suggest_sharing(pods), indent=2))
PY

# 4) Carbon-Aware Scheduler scaffold
cat > megamoots_v5/carbon/carbon_scheduler.py <<'PY'
"""
Carbon-Aware Scheduler
Given a job with flexibility window, propose run times to minimize carbon intensity.
This uses a placeholder hourly carbon index (0..100) - lower is greener.
"""
from typing import Dict, Any, List
import datetime

# placeholder carbon index for next 24 hours (lower is greener)
CARBON_INDEX = [50,45,40,35,30,25,28,32,40,55,65,70,75,80,78,70,65,60,55,50,48,46,47,49]

def best_run_slots(flex_hours:int, earliest:datetime.datetime=None) -> Dict[str,Any]:
    # returns the best contiguous window of flex_hours with lowest avg carbon index
    if earliest is None:
        earliest = datetime.datetime.utcnow()
    start_hour = earliest.hour
    candidates = []
    for offset in range(0, 24):
        idx = (start_hour + offset) % 24
        if idx + flex_hours > 24:
            continue
        window = CARBON_INDEX[idx:idx+flex_hours]
        avg = sum(window)/len(window)
        candidates.append((idx, avg, window))
    if not candidates:
        return {"error":"no-window-found"}
    best = min(candidates, key=lambda x: x[1])
    return {"start_hour_utc": best[0], "avg_carbon": round(best[1],1), "window": best[2]}

if __name__ == "__main__":
    import json, datetime
    print(json.dumps(best_run_slots(4), indent=2))
PY

# 5) Demo runner that calls all modules
cat > demo_v5/finops_trader_full.py <<'PY'
#!/usr/bin/env python3
"""
Demo runner that combines recommender, cost preview, sharing optimizer, and carbon scheduler
Usage: PYTHONPATH=. python demo_v5/finops_trader_full.py
"""
import json
from megamoots_v5.recommender.recommender import recommend
from megamoots_v5.cost_preview.cost_preview import cost_preview
from megamoots_v5.sharing.sharing_optimizer import suggest_sharing
from megamoots_v5.carbon.carbon_scheduler import best_run_slots
import datetime

def main():
    job = {"work_units": 12, "base_hours": 2.0, "mem_required_gb": 32}
    print("=== GPU Recommender ===")
    rec = recommend(job)
    print(json.dumps(rec, indent=2))
    print("\n=== Cost Preview ===")
    job_spec = {"gpu_type": rec['choice']['gpu'], "gpus": 8, "est_hours_per_gpu": rec['choice']['est_hours'], "checkpoint_overhead_pct":0.03}
    cp = cost_preview(job_spec)
    print(json.dumps(cp, indent=2))
    print("\n=== Sharing Optimizer ===")
    pods=[{"name":"train-A","mem_gb":20,"avg_util_pct":22},{"name":"infer-B","mem_gb":12,"avg_util_pct":18}]
    sh = suggest_sharing(pods, gpu_capacity_gb=80)
    print(json.dumps(sh, indent=2))
    print("\n=== Carbon Scheduler ===")
    cs = best_run_slots(4, datetime.datetime.utcnow())
    print(json.dumps(cs, indent=2))

if __name__=="__main__":
    main()
PY
chmod +x demo_v5/finops_trader_full.py

# 6) Small CLI wrapper
cat > demo_v5/run_v5_demo.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
echo "Running MegaMoats v5 FinOps demo (fake-mode)"
PYTHON=${PYTHON:-python}
PYTHONPATH=. "$PYTHON" demo_v5/finops_trader_full.py
SH
chmod +x demo_v5/run_v5_demo.sh

# 7) README
cat > docs_v5/README_V5.md <<'MD'
# MegaMoats v5 — Feature Pack

This pack contains scaffolds for:
- GPU Recommender (type & cost vs performance)
- Training Job Cost Preview (spot vs on-demand)
- GPU Sharing Intelligence (MIG/MPS recommendations)
- Carbon-Aware Scheduler (green scheduling suggestions)

How to run (fake-mode):
  PYTHONPATH=. python demo_v5/finops_trader_full.py
or:
  ./demo_v5/run_v5_demo.sh

Notes:
- Replace static price catalog and carbon index with your live oracles/APIs.
- Plug real telemetry, NVML and cloud APIs to enable "real mode".
MD

# 8) git hint to add & commit (just printed; not auto-committed)
echo
echo "Created files under megamoots_v5/ demo_v5/ docs_v5/. To add & push:"
echo "  git add megamoots_v5 demo_v5 docs_v5 create_megamoots_v5_pack.sh"
echo "  git commit -m \"Add MegaMoats v5 feature pack: recommender, cost preview, sharing, carbon scheduler\""
echo "  git push --set-upstream origin megamoats-v5-finops"
echo
echo "Demo run: PYTHONPATH=. python demo_v5/finops_trader_full.py"
