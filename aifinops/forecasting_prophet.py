from __future__ import annotations
from typing import List, Tuple
import pandas as pd
import datetime as dt
from prophet import Prophet
from .aws_cost_fetcher import CostItem

def prophet_forecast(items: List[CostItem], days_ahead: int = 14) -> List[Tuple[str, float]]:
    """
    Fit a Prophet model on daily aggregated costs and return a days_ahead forecast.
    Returns list of (date_iso, predicted_value).
    """
    df = pd.DataFrame([{"date": i.date, "amount": i.amount} for i in items])
    if df.empty:
        today = dt.date.today()
        return [((today + dt.timedelta(days=i)).isoformat(), 0.0) for i in range(1, days_ahead + 1)]

    df["ds"] = pd.to_datetime(df["date"])
    df = df.groupby("ds")["amount"].sum().reset_index()
    df = df.rename(columns={"amount": "y"})

    # Fit Prophet model (simple, no holidays)
    m = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)
    try:
        m.fit(df)
    except Exception as e:
        # If Prophet fails, fallback to flat forecast
        last = float(df["y"].iloc[-1]) if not df.empty else 0.0
        today = df["ds"].iloc[-1].date() if not df.empty else dt.date.today()
        return [((today + dt.timedelta(days=i)).isoformat(), float(last)) for i in range(1, days_ahead + 1)]

    future = m.make_future_dataframe(periods=days_ahead, freq="D")
    fc = m.predict(future)
    pred = fc[["ds", "yhat"]].tail(days_ahead)
    res = [(row["ds"].date().isoformat(), float(row["yhat"])) for _, row in pred.iterrows()]
    return res
