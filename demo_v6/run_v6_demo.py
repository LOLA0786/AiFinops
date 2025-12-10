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
