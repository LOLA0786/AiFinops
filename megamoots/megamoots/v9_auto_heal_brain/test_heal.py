from megamoots.v9_auto_heal_brain.heal import plan_heal

def test_plan():
    ev = [{"name":"a","restarts":4},{"name":"b","restarts":1}]
    out = plan_heal(ev)
    assert len(out["restart"]) == 1
