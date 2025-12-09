from __future__ import annotations
from typing import List, Tuple
import random

from .aws_cost_fetcher import CostItem

# Minimal mappings (extendable)
FAMILY_SPOT_SAVINGS = {
    "p4": 0.6,
    "p3": 0.6,
    "g4": 0.65,
    "g5": 0.6,
    "c5": 0.7,
    "m5": 0.7,
    "r5": 0.7,
    "t3": 0.8
}

def estimate_spot_savings(items: List[CostItem], svc_name: str = "AmazonEC2") -> Tuple[float, str]:
    """
    Heuristic: assume some percent of EC2 spend is spot-eligible and multiply by family factor.
    """
    total = sum(i.amount for i in items if svc_name in i.service)
    if total == 0:
        return 0.0, "No EC2 spend found."
    # guess % spot-eligible
    eligible_pct = 0.5  # default 50% eligible
    # average family factor
    avg_factor = sum(FAMILY_SPOT_SAVINGS.values()) / len(FAMILY_SPOT_SAVINGS)
    savings = total * eligible_pct * avg_factor
    note = f"Assuming {int(eligible_pct*100)}% of EC2 is spot-eligible and avg spot discount {int(avg_factor*100)}% -> est. savings ${savings:.2f}"
    return savings, note

def recommend_spot_mix(items: List[CostItem], svc_name: str = "AmazonEC2") -> List[str]:
    """
    Produce textual recommendations; in real system we'd inspect instance inventory.
    """
    # example rules
    recs = [
        "Migrate batch & stateless worker fleets to Spot with checkpointing.",
        "Use mixed instance policies in ASG with max price caps.",
        "Reserve a small base of on-demand for critical control-plane nodes; convert rest to spot."
    ]
    return recs
