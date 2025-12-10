from megamoots.v3_cluster_dna.signature_impl import signature_from_metrics, similarity
def test_signature_similarity():
    a = signature_from_metrics({"nodes":2,"avg_gpu_util":50})
    b = signature_from_metrics({"nodes":2,"avg_gpu_util":50})
    assert similarity(a,b) > 0.9
