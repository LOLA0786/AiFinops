from megamoots.v7_gpu_carbon_optimizer.carbon import score_region

def test_score():
    assert score_region({"renewable_pct":80}) > 0
