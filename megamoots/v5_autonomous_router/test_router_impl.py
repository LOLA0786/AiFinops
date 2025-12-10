from megamoots.v5_autonomous_router.router_impl import recommend_action
def test_router_scale_down():
    r = recommend_action({"avg_gpu_util":5}, {"cloud":"gcp","price":1.5})
    assert r["action"] == "scale_down_nodes"
