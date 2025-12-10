"""
GPU Telemetry - production-ish implementation.

Features:
- Uses NVML if available, else falls back to simulated adapter
- Batches telemetry and writes to local queue file (simulates uploader)
- Pluggable uploader interface
"""
import time
import json
import os
import threading
from collections import deque

# Try to import NVML (optional). If not present, we use the simulator adapter.
try:
    import pynvml
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False

class NVMLAdapter:
    def __init__(self):
        pynvml.nvmlInit()
        self.count = pynvml.nvmlDeviceGetCount()

    def sample_once(self):
        out = []
        for i in range(self.count):
            h = pynvml.nvmlDeviceGetHandleByIndex(i)
            util = pynvml.nvmlDeviceGetUtilizationRates(h)
            meminfo = pynvml.nvmlDeviceGetMemoryInfo(h)
            out.append({
                "gpu_index": i,
                "gpu_util": int(util.gpu),
                "mem_used": int(meminfo.used/1024/1024),
                "mem_total": int(meminfo.total/1024/1024),
                "temp": 0
            })
        return out

class SimAdapter:
    "Simple deterministic simulator for telemetry"
    def __init__(self, node_id="node-1", seed=1):
        import random
        self.node_id = node_id
        self.r = random.Random(seed)
    def sample_once(self):
        return [{
            "gpu_index": 0,
            "gpu_util": max(0, min(100, int(self.r.gauss(60,15)))),
            "mem_used": int(abs(self.r.gauss(12000,2000))),
            "mem_total": 32768,
            "temp": int(self.r.uniform(40,85))
        }]

class TelemetryPublisher:
    def __init__(self, out_path="telemetry_queue.jsonl", batch=10):
        self.out_path = out_path
        self.batch = batch
        self.buf = deque()
        self.lock = threading.Lock()

    def publish(self, item):
        with self.lock:
            self.buf.append(item)
            if len(self.buf) >= self.batch:
                self.flush()

    def flush(self):
        with open(self.out_path, "a") as f:
            while self.buf:
                it = self.buf.popleft()
                f.write(json.dumps(it) + "\\n")

def run_collector(adapter, publisher, interval=1.0, count=None):
    i = 0
    while True:
        samples = adapter.sample_once()
        ts = int(time.time())
        for s in samples:
            s.update({"ts": ts})
            publisher.publish(s)
        i += 1
        if count and i >= count:
            publisher.flush()
            break
        time.sleep(interval)

if __name__ == "__main__":
    adapter = NVMLAdapter() if NVML_AVAILABLE else SimAdapter(node_id="node-sim", seed=42)
    pub = TelemetryPublisher(out_path="sim/telemetry_queue.jsonl", batch=5)
    run_collector(adapter, pub, interval=0.5, count=40)
