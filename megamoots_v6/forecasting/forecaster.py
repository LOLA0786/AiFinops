import random
import datetime as dt

def forecast_cost(history):
    """
    History: list of hourly cost numbers
    Returns next 24-hour forecast
    """
    avg = sum(history[-24:]) / 24 if len(history) >= 24 else sum(history)/len(history)
    drift = random.uniform(-0.05, 0.05)
    next_day = [round(avg * (1+drift) * random.uniform(0.97,1.04), 2) for _ in range(24)]
    return {
        "forecast": next_day,
        "expected_monthly": round(sum(next_day)*30, 2),
        "risk": random.choice(["low", "medium", "high"])
    }
