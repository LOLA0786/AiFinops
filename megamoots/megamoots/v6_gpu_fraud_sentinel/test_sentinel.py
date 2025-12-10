from megamoots.v6_gpu_fraud_sentinel.sentinel import detect_anomaly

def test_detect():
    s = [{"gpu_util":100},{"gpu_util":50}]
    out = detect_anomaly(s)
    assert len(out) == 1
