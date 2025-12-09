import random
import time

class TelemetryClient:
    def __init__(self, endpoint=None):
        self.endpoint = endpoint or "http://localhost:8080/gpu"

    def sample(self):
        return {
            "gpu_util": random.randint(0,100),
            "mem_used": random.randint(0,32000),
            "mem_total": 32768,
            "timestamp": int(time.time())
        }

    def push(self, payload):
        print("[telemetry] push ->", payload)
