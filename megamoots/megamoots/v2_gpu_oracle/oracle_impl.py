"""
GPU Price Oracle - simple real logic:
- Normalizes prices from multiple 'providers' (pluggable)
- Keeps a sliding window of recent prices
- Exposes query functions
"""
import time, threading
from collections import defaultdict, deque

class PriceOracle:
    def __init__(self, window_seconds=300):
        self.window = window_seconds
        self.lock = threading.Lock()
        self.prices = defaultdict(lambda: deque())  # (gpu_type)->deque of (ts, price, cloud)

    def ingest(self, cloud, gpu_type, price, ts=None):
        ts = ts or time.time()
        with self.lock:
            dq = self.prices[gpu_type]
            dq.append((ts, price, cloud))
            # trim
            cutoff = ts - self.window
            while dq and dq[0][0] < cutoff:
                dq.popleft()

    def get_snapshot(self):
        out = {}
        with self.lock:
            for gpu, dq in self.prices.items():
                out[gpu] = [{"ts": t, "price": p, "cloud": c} for (t,p,c) in dq]
        return out

    def find_best(self, gpu_type="A100"):
        with self.lock:
            dq = self.prices.get(gpu_type, [])
            if not dq:
                return None
            best = min(dq, key=lambda r: r[1])
            return {"cloud": best[2], "price": best[1], "ts": best[0]}
