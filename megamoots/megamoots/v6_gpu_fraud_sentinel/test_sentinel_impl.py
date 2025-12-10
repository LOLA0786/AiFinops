from megamoots.v6_gpu_fraud_sentinel.sentinel_impl import detect_anomalies
def test_detect():
    s = [10,12,11,1000]
    out = detect_anomalies(s, z_thresh=2.5)
    assert 1000 in out
