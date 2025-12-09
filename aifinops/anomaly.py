from __future__ import annotations
from typing import List, Dict
import collections
import statistics

from .aws_cost_fetcher import CostItem

def detect_anomalies(items: List[CostItem], z_thresh: float = 2.0) -> Dict[str, List[CostItem]]:
    """
    Return dict service -> list of anomalous CostItems based on z-score on amounts.
    """
    by_service = collections.defaultdict(list)
    for it in items:
        by_service[it.service].append(it)

    anomalies = {}
    for svc, lst in by_service.items():
        amounts = [x.amount for x in lst]
        if len(amounts) < 2:
            continue
        mean = statistics.mean(amounts)
        stdev = statistics.pstdev(amounts) if len(amounts) > 1 else 0
        if stdev == 0:
            continue
        out = []
        for x in lst:
            z = (x.amount - mean) / stdev
            if abs(z) >= z_thresh:
                out.append(x)
        if out:
            anomalies[svc] = out
    return anomalies
