from megamoots.v9_auto_heal_brain.heal_impl import plan_heal
def test_heal_actions():
    ev = [{"name":"x","restarts":4},{"name":"y","oom":True}]
    out = plan_heal(ev)
    assert any(a["type"]=="restart_pod" for a in out)
