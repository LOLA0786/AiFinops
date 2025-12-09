from megamoots.cluster_dna.signature import signature_from_metrics

def test_signature():
    s = signature_from_metrics({"nodes":2,"avg_gpu_util":50})
    assert s["nodes"] == 2
