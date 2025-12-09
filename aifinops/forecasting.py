from __future__ import annotations
from typing import List, Tuple
import pandas as pd
import numpy as np
import datetime as dt

from .aws_cost_fetcher import CostItem

def daily_series(items: List[CostItem]) -> pd.Series:
    df = pd.DataFrame([{"date": i.date, "amount": i.amount} for i in items])
    if df.empty:
        return pd.Series(dtype=float)
    df = df.groupby("date")["amount"].sum().reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D").fillna(0)
    return df["amount"]

def simple_moving_average_forecast(series: pd.Series, days_ahead: int = 14, window: int = 7) -> List[Tuple[str, float]]:
    if series.empty:
        today = dt.date.today()
        return [( (today + dt.timedelta(days=i)).isoformat(), 0.0) for i in range(1, days_ahead+1)]
    sma = series.rolling(window=window, min_periods=1).mean()
    last = sma.iloc[-1]
    forecast = [ ( (series.index[-1].date() + dt.timedelta(days=i)).isoformat(), float(last) ) for i in range(1, days_ahead+1) ]
    return forecast

def seasonal_adjusted_forecast(series: pd.Series, days_ahead: int = 14) -> List[Tuple[str, float]]:
    """
    Very simple seasonality: use weekly seasonality averages + sma.
    """
    if series.empty:
        today = dt.date.today()
        return [( (today + dt.timedelta(days=i)).isoformat(), 0.0) for i in range(1, days_ahead+1)]
    df = series.reset_index()
    df["dow"] = df["date"].dt.dayofweek
    weekly = df.groupby("dow")[0].mean().to_dict()
    last_date = series.index[-1].date()
    forecast = []
    for i in range(1, days_ahead+1):
        d = last_date + dt.timedelta(days=i)
        base = weekly.get(d.weekday(), series.mean())
        forecast.append((d.isoformat(), float(base)))
    return forecast
