from __future__ import annotations
from typing import List, Dict, Any
import boto3
import datetime as dt
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def fetch_gpu_utilization(instance_id: str, minutes: int = 60, region: str = "us-east-1") -> float:
    try:
        cw = boto3.client("cloudwatch", region_name=region)
        end = dt.datetime.utcnow()
        start = end - dt.timedelta(minutes=minutes)
        resp = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="GPUUtilization",  # note: metric name depends on driver/agent; might be different
            Dimensions=[{"Name":"InstanceId","Value":instance_id}],
            StartTime=start, EndTime=end, Period=60, Statistics=["Average"]
        )
        dps = resp.get("Datapoints", [])
        if not dps:
            return 0.0
        return float(sorted(dps, key=lambda d: d["Timestamp"])[-1].get("Average", 0.0))
    except (NoCredentialsError, PartialCredentialsError, ClientError):
        return 0.0

def build_gpu_heatmap(instance_ids: List[str], minutes: int = 60, region: str = "us-east-1") -> Dict[str, float]:
    out = {}
    for iid in instance_ids:
        out[iid] = fetch_gpu_utilization(iid, minutes=minutes, region=region)
    return out
