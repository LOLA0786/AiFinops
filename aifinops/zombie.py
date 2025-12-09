from __future__ import annotations
from typing import List, Dict
from .aws_cost_fetcher import CostItem

def find_zombies(items: List[CostItem]) -> List[Dict]:
    """
    Returns detected 'zombie resources' as dicts with reason.
    This scaffold checks very small-cost items as candidates.
    """
    zombies = []
    for it in items:
        if it.amount < 0.01:  # threshold example
            zombies.append({"service": it.service, "date": it.date, "amount": it.amount, "reason":"very low cost; possible orphan"})
    return zombies
