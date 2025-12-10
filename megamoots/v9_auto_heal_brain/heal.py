def plan_heal(events):
    # simplistic policy: restart pods that failed more than 3 times
    return {"restart": [e for e in events if e.get("restarts",0)>3]}
