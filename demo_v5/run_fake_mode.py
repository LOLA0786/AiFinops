from megamoots_v5.telemetry.collector import collect_realtime_telemetry
from megamoots_v5.profiler.pytorch_profiler import run_model_profiler
from megamoots_v5.scheduler.decision import scheduler_decision
from megamoots_v5.cost_engine.optimizer import evaluate_cost

print("=== MegaMoats v5 DEMO (FAKE MODE) ===")

t = collect_realtime_telemetry()
p = run_model_profiler()
c = evaluate_cost()
s = scheduler_decision()

print("Telemetry:", t)
print("Profiler:", p)
print("Cost Engine:", c)
print("Scheduler:", s)
