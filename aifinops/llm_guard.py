from __future__ import annotations
import os

def monitor_llm_costs(llm_metrics: dict, limit_monthly: float = 1000.0) -> dict:
    """
    Check current token spend and raise alerts if above thresholds.
    llm_metrics example: {'openai': 120.0, 'xai': 50.0}
    """
    alerts = {}
    total = sum(llm_metrics.values())
    if total > limit_monthly:
        alerts['limit_exceeded'] = True
        alerts['monthly_spend'] = total
    else:
        alerts['limit_exceeded'] = False
        alerts['monthly_spend'] = total
    return alerts
