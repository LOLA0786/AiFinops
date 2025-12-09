from __future__ import annotations
from typing import List
import datetime as dt
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def average_cpu_for_instance(instance_id: str, minutes: int = 60, region: str = "us-east-1") -> float:
    try:
        cw = boto3.client("cloudwatch", region_name=region)
        end = dt.datetime.utcnow()
        start = end - dt.timedelta(minutes=minutes)
        resp = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=60 * max(1, minutes // 5),
            Statistics=["Average"],
        )
        dps = resp.get("Datapoints", [])
        if not dps:
            return 0.0
        return float(sorted(dps, key=lambda d: d["Timestamp"])[-1].get("Average", 0.0))
    except (NoCredentialsError, PartialCredentialsError, ClientError):
        return 0.0

def find_low_cpu_instances(region: str = "us-east-1", minutes: int = 60, threshold: float = 5.0) -> List[dict]:
    try:
        ec2 = boto3.client("ec2", region_name=region)
    except (NoCredentialsError, PartialCredentialsError):
        return []

    out = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate(Filters=[{"Name":"instance-state-name","Values":["running"]}]):
        for r in page.get("Reservations", []):
            for inst in r.get("Instances", []):
                iid = inst.get("InstanceId")
                itype = inst.get("InstanceType")
                avg = average_cpu_for_instance(iid, minutes=minutes, region=region)
                if avg < threshold:
                    out.append({"InstanceId": iid, "InstanceType": itype, "AvgCPU": avg})
    return out
