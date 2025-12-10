"""
Cluster DNA: produce compact signatures and fingerprint similarity
- uses simple hashing of sorted metrics
- supports comparison distance via Jaccard-like measure
"""
import hashlib
import json

def signature_from_metrics(metrics: dict):
    # canonicalize keys & compute a short sha256
    keys = sorted(metrics.items())
    s = json.dumps(keys, separators=(",",":"), sort_keys=True)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
    return {"signature": h, "summary": metrics}

def similarity(sigA, sigB):
    # trivial equality-based similarity or Hamming distance on hex
    a = sigA["signature"]
    b = sigB["signature"]
    # compute normalized Hamming distance on hex chars
    dist = sum(1 for x,y in zip(a,b) if x!=y) / max(len(a), len(b))
    return 1.0 - dist
