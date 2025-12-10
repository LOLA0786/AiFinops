"""
Auto-heal policy engine.
- Detects pod crash loops and suggests remediation actions.
"""
def plan_heal(events):
    actions = []
    for e in events:
        if e.get("restarts",0) > 3:
            actions.append({"type":"restart_pod","pod":e["name"]})
        if e.get("oom",False):
            actions.append({"type":"scale_down_batch","pod":e["name"]})
    return actions
