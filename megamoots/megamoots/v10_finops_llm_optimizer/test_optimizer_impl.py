from megamoots.v10_finops_llm_optimizer.optimizer_impl import suggest_changes
def test_optimizer():
    out = suggest_changes({"monthly":20000},{"avg_gpu_util":10})
    assert "consider_spot_instances" in out
