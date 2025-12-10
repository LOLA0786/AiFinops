#!/bin/bash
set -euo pipefail
echo "Starting local demo: generating synthetic data and running simple pipelines"
python3 -u sim/simulator.py &

echo "Running telemetry collector to read sim output and push into oracle/consumers..."
python3 - <<'PY'
import time, json
from megamoots.v2_gpu_oracle.oracle_impl import PriceOracle
from megamoots.v1_gpu_telemetry.telemetry_impl import SimAdapter, TelemetryPublisher, run_collector
from megamoots.v2_gpu_oracle.oracle_impl import PriceOracle

# Wait for sim to seed
time.sleep(1)
oracle = PriceOracle(window_seconds=600)
# ingest price signals from sim/output/market_signals.jsonl
with open("sim/output/market_signals.jsonl") as f:
    for line in f:
        try:
            d=json.loads(line)
            oracle.ingest(d["cloud"], "A100", d["price"], ts=d["ts"])
        except:
            pass

print("Oracle snapshot:", oracle.get_snapshot().get("A100",[])[:3])

# Run telemetry reader - simply read telemetry file and print cluster signature
samples=[]
with open("sim/output/telemetry.jsonl") as f:
    for i,line in enumerate(f):
        if i>200: break
        samples.append(json.loads(line))
# compute avg util
avg_util = sum(s["gpu_util"] for s in samples)/len(samples)
print("Avg GPU util (sim):", avg_util)
PY

echo "Local demo complete."
