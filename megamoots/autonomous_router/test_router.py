from megamoots.autonomous_router.router import recommend_action

def test_recommend():
    assert recommend_action({"avg_gpu_util":5}, ("gcp",2.9))["action"] == "scale_down_nodes"
