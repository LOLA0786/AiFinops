from megamoots.v7_gpu_carbon_optimizer.carbon_impl import score_region
def test_carbon_score():
    assert score_region({"renewable_pct":80,"carbon_intensity":100}) < score_region({"renewable_pct":20,"carbon_intensity":300})
