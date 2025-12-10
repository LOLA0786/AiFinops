from megamoots.v10_finops_llm_optimizer.optimizer import suggest_changes

def test_suggest():
    assert "use_spot" in suggest_changes({"monthly":20000},{})
