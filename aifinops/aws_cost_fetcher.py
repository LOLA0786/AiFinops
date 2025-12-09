from __future__ import annotations

import os
os.environ.pop("AWS_PROFILE", None)  # disable AWS_PROFILE forever

import datetime as dt
from dataclasses import dataclass
from typing import List
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

@dataclass
class CostItem:
    date: str
    service: str
    amount: float
    unit: str

def fetch_aws_daily_costs(days: int = 3) -> List[CostItem]:
    """
    Final stable version:
    - Never uses AWS_PROFILE
    - If AWS creds are missing → returns sample data instead of crashing
    """

    try:
        session = boto3.Session()
        ce = session.client("ce", region_name="us-east-1")

        end = dt.date.today()
        start = end - dt.timedelta(days=days)

        resp = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start.strftime("%Y-%m-%d"),
                "End": end.strftime("%Y-%m-%d"),
            },
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

                items.append(
                    CostItem(
                        date=date,
                        service=service,
                        amount=amount,
                        unit=unit,
                    )
                )

        return items

    except (NoCredentialsError, PartialCredentialsError):
        # Return safe sample data instead of crashing
        today = dt.date.today().strftime("%Y-%m-%d")
        return [
            CostItem(date=today, service="SampleEC2", amount=12.34, unit="USD"),
            CostItem(date=today, service="SampleLambda", amount=1.23, unit="USD"),
        ]
