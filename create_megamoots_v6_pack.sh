#!/usr/bin/env bash
set -e

echo "=== Generating MegaMoats v6 Pack ==="

mkdir -p megamoots_v6/{forecasting,recommender,carbon_scheduler,topology,job_preview}
mkdir -p demo_v6

###############################################
# 1. COST FORECASTING ENGINE
###############################################
cat <<'PYEOF' > megamoots_v6/forecasting/forecaster.py
import random
import datetime as dt

def forecast_cost(history):
    """
    History: list of hourly cost numbers
    Returns next 24-hour forecast
    """
    avg = sum(history[-24:]) / 24 if len(history) >= 24 else sum(history)/len(history)
    drift = random.uniform(-0.05, 0.05)
    next_day = [round(avg * (1+drift) * random.uniform(0.97,1.04), 2) for _ in range(24)]
    return {
        "forecast": next_day,
        "expected_monthly": round(sum(next_day)*30, 2),
        "risk": random.choice(["low", "medium", "high"])
    }
PYEOF

###############################################
# 2. GPU RECOMMENDER SYSTEM
###############################################
cat <<'PYEOF' > megamoots_v6/recommender/recommender.py
def recommend_gpu(model_size_gb, batch_size, training_hours):
    # Simple heuristic for demo
    if model_size_gb > 80:
        return "H100 80GB", "Best for extremely large models"
    if model_size_gb > 40:
        return "A100 80GB", "Balanced memory + throughput"
    if batch_size < 32:
        return "A10G", "Cost efficient for smaller models"
    return "A100 40GB", "General-purpose high-performance choice"
PYEOF

###############################################
# 3. CARBON-AWARE SCHEDULER
###############################################
cat <<'PYEOF' > megamoots_v6/carbon_scheduler/scheduler.py
import random

def carbon_optimize(job_name):
    low_carbon_hours = random.randint(1,6)
    recommendation = f"Delay {job_name} by {low_carbon_hours}h to run on low-carbon window"
    carbon_savings = round(random.uniform(0.5,3.4), 2)
    return {
        "recommendation": recommendation,
        "carbon_savings_tons": carbon_savings
    }
PYEOF

###############################################
# 4. GPU TOPOLOGY ANALYZER
###############################################
cat <<'PYEOF' > megamoots_v6/topology/analyzer.py
import random

def analyze_topology():
    """
    Fake topology: NVLink connections, PCIe lanes, multi-GPU bandwidth
    """
    return {
        "num_gpus": 8,
        "nvlink_matrix": [[random.randint(0,1) for _ in range(8)] for _ in range(8)],
        "pcie_bandwidth_gbps": random.randint(128, 256),
        "bottleneck": random.choice(["PCIe bottleneck", "NVLink imbalance", "None"])
    }
PYEOF

###############################################
# 5. JOB COST PREVIEW ENGINE
###############################################
cat <<'PYEOF' > megamoots_v6/job_preview/preview.py
def preview_job(model_name, hours, gpu_type="A100"):
    gpu_cost_map = {"A100": 4.2, "H100": 6.8, "A10G": 1.9}
    rate = gpu_cost_map.get(gpu_type, 4.0)
    total = round(rate * hours * 8, 2) # assume 8 GPUs
    return {
        "model": model_name,
        "gpu_type": gpu_type,
        "expected_duration_hours": hours,
        "cost_estimate": total,
        "recommendation": "Use spot + checkpointing to reduce 40-60% cost"
    }
PYEOF

###############################################
# 6. DEMO CLI
###############################################
cat <<'PYEOF' > demo_v6/run_v6_demo.py
import random, time
from megamoots_v6.forecasting.forecaster import forecast_cost
from megamoots_v6.recommender.recommender import recommend_gpu
from megamoots_v6.carbon_scheduler.scheduler import carbon_optimize
from megamoots_v6.topology.analyzer import analyze_topology
from megamoots_v6.job_preview.preview import preview_job

line = lambda: "━" * 60

def main():
    print(line())
    print(" AI FinOps OS — MegaMoats v6 Demo")
    print(line())

    # Forecasting
    history = [random.uniform(2.5,6.0) for _ in range(100)]
    f = forecast_cost(history)
    print("\n[1] Cost Forecasting ML")
    print("  Expected monthly:", f["expected_monthly"], "USD")
    print("  Risk Level:", f["risk"])

    # GPU recommender
    rec = recommend_gpu(60, 64, 12)
    print("\n[2] GPU Recommender")
    print("  GPU:", rec[0])
    print("  Reason:", rec[1])

    # Carbon-aware scheduling
    car = carbon_optimize("TrainingJob-42")
    print("\n[3] Carbon-Aware Scheduler")
    print("  Recommendation:", car["recommendation"])
    print("  CO2 Saved:", car["carbon_savings_tons"], "tons")

    # Topology analyzer
    topo = analyze_topology()
    print("\n[4] GPU Topology Analyzer")
    print("  GPUs:", topo["num_gpus"])
    print("  Bottleneck:", topo["bottleneck"])

    # Job preview engine
    job = preview_job("GPT-3 small", 14, "A100")
    print("\n[5] Job Cost Preview")
    print("  Estimated Cost:", job["cost_estimate"], "USD")
    print("  Recommendation:", job["recommendation"])

    print("\n" + line())
    print(" MegaMoats v6 Demo Completed")
    print(line())

if __name__ == "__main__":
    main()
PYEOF

chmod +x create_megamoots_v6_pack.sh
echo "=== MegaMoats v6 Pack Generated ==="
