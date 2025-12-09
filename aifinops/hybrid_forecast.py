from __future__ import annotations
from typing import List, Tuple
import pandas as pd

def hybrid_forecast(series: pd.Series, days_ahead: int = 14) -> List[Tuple[str,float]]:
    """
    Placeholder for Prophet+LSTM hybrid model. Returns flat forecast currently.
    """
    if series.empty:
        return []
    last = float(series.iloc[-1])
    res = []
    last_date = series.index[-1].date()
    for i in range(1, days_ahead+1):
        res.append(((last_date + __import__('datetime').timedelta(days=i)).isoformat(), last))
    return res
