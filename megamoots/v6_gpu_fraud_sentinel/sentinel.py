def detect_anomaly(samples):
    # placeholder heuristic
    suspicious = [s for s in samples if s.get("gpu_util",0) > 99]
    return suspicious
