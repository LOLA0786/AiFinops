from megamoots.v3_cluster_dna.signature import signature_from_metrics

def test_signature():
    s = signature_from_metrics({"nodes":2,"avg_gpu_util":50, "mem_pressure": 0.1})
    assert s["nodes"] == 2
