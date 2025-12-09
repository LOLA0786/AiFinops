from __future__ import annotations
from typing import List, Tuple
import datetime as dt
from .aws_cost_fetcher import CostItem

def predict_idle_windows(items: List[CostItem], lookahead_days: int = 7) -> List[Tuple[str, float]]:
    """
    Very simple predictor: returns list of (date_iso, est_idle_probability) for next lookahead days.
    Replace with time-series model in production.
    """
    today = dt.date.today()
    return [((today + dt.timedelta(days=i)).isoformat(), 0.1 * (i%3)) for i in range(1, lookahead_days+1)]
