from __future__ import annotations
from typing import List
import os
from .actions import stop_instances
from .utilization import find_low_cpu_instances

def ui_stop_idle_instances(region: str = "us-east-1", minutes: int = 60, threshold: float = 5.0, apply: bool = False):
    """
    Safe UI wrapper — returns candidates and dry-run results.
    Requires CONFIRM_AUTO_ACTIONS=true to allow apply=True.
    """
    confirm = os.getenv("CONFIRM_AUTO_ACTIONS", "false").lower() in ("1","true","yes")
    candidates = find_low_cpu_instances(region=region, minutes=minutes, threshold=threshold)
    ids = [c["InstanceId"] for c in candidates]
    if not ids:
        return {"candidates": [], "results": []}
    if not apply:
        return {"candidates": ids, "results": [{"instance_id": ii, "action": "dry-run"} for ii in ids]}
    if apply and not confirm:
        raise PermissionError("Auto actions disabled. Set CONFIRM_AUTO_ACTIONS=true in .env to allow apply.")
    # call stop_instances (dry_run False will actually stop)
    results = stop_instances(ids, dry_run=not apply)
    return {"candidates": ids, "results": [r.__dict__ for r in results]}
