from __future__ import annotations
from typing import Dict

def compute_profitability(costs: Dict[str,float], revenues: Dict[str,float]) -> Dict[str,float]:
    """
    Map cost buckets -> revenue and compute margin.
    """
    total_cost = sum(costs.values())
    total_rev = sum(revenues.values())
    margin = (total_rev - total_cost) / total_rev * 100 if total_rev else 0.0
    return {"total_cost": total_cost, "total_revenue": total_rev, "margin_pct": margin}
