from __future__ import annotations
from typing import List, Dict, Tuple
from .aws_cost_fetcher import CostItem

def attribute_costs(items: List[CostItem]) -> Dict[str, float]:
    """
    Simple attribution engine:
    - Use service name heuristics and tags (if available).
    - Returns dictionary: bucket -> cost
    """
    buckets = {}
    for it in items:
        key = "Unallocated"
        s = it.service.lower()
        if "ec2" in s or "instance" in s:
            key = "Compute"
        elif "s3" in s or "glacier" in s:
            key = "Storage"
        elif "lambda" in s:
            key = "Serverless"
        else:
            key = "Other"
        buckets[key] = buckets.get(key, 0.0) + it.amount
    return buckets

def suggest_tags_for_unallocated(items: List[CostItem]) -> Dict[str, str]:
    """
    Lightweight heuristic: suggest tags for resources that seem unallocated.
    """
    return {"cost_center": "UNKNOWN", "team": "UNKNOWN"}
