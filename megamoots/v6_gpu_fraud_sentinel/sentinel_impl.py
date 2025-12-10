"""
Fraud sentinel using z-score anomaly detection over windows.
"""
import statistics, math

def detect_anomalies(samples, z_thresh=3.0):
    # samples: list of numeric
    if len(samples) < 2:
        return []
    mean = statistics.mean(samples)
    stdev = statistics.pstdev(samples)
    if stdev == 0:
        return []
    return [x for x in samples if abs((x-mean)/stdev) > z_thresh]
