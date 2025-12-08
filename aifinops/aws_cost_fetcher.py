from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List

import boto3

from .config import get_settings

@dataclass
class CostItem:
    date: str
    service: str
    amount: float
    unit: str
    usage_type: str | None = None

def fetch_aws_daily_costs(days: int = 3) -> List[CostItem]:
    """V1 – minimal AWS Cost Explorer reader (by Service, last N days)."""
    settings = get_settings()
    session_kwargs = {}
    if settings.aws_profile:
        session_kwargs["profile_name"] = settings.aws_profile
    session = boto3.Session(**session_kwargs)
    ce = session.client("ce", region_name="us-east-1")

    end = dt.date.today()
    start = end - dt.timedelta(days=days)

    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start.strftime("%Y-%m-%d"), "End": end.strftime("%Y-%m-%d")},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    items: List[CostItem] = []
    for day in resp.get("ResultsByTime", []):
        date = day["TimePeriod"]["Start"]
        for group in day.get("Groups", []):
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            unit = group["Metrics"]["UnblendedCost"]["Unit"]
            service = group["Keys"][0]
            items.append(CostItem(date=date, service=service, amount=amount, unit=unit))
    return items
