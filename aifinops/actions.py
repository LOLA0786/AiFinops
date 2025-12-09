from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from .config import get_settings

GPU_FAMILIES = ("p2", "p3", "p4", "p5", "g3", "g4", "g5", "g6")

@dataclass
class InstanceActionResult:
    instance_id: str
    instance_type: str
    action: str
    reason: str

def _get_boto3_clients():
    settings = get_settings()
    try:
        session = boto3.Session()
        ec2 = session.client("ec2", region_name=settings.aws_region)
        cw = session.client("cloudwatch", region_name=settings.aws_region)
        return ec2, cw
    except (NoCredentialsError, PartialCredentialsError):
        return None, None

def list_gpu_instances() -> List[dict]:
    """
    Return running GPU instances (by instance type prefix like p3, g5, etc.)
    """
    ec2, _ = _get_boto3_clients()
    if not ec2:
        return []

    instances: List[dict] = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    ):
        for reservation in page.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                itype = inst.get("InstanceType", "")
                if any(itype.startswith(prefix) for prefix in GPU_FAMILIES):
                    instances.append(inst)
    return instances

def _avg_cpu_for_instance(cw, instance_id: str, minutes: int = 30) -> float:
    """
    Average CPUUtilization over the last N minutes.
    """
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(minutes=minutes)
    try:
        resp = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=max(60, minutes * 60 // 5),
            Statistics=["Average"],
        )
        datapoints = resp.get("Datapoints", [])
        if not datapoints:
            return 0.0
        # Take the latest datapoint
        latest = sorted(datapoints, key=lambda d: d["Timestamp"])[-1]
        return float(latest.get("Average", 0.0))
    except ClientError:
        return 0.0

def find_idle_gpus(threshold_minutes: int = 30, cpu_threshold: float = 5.0) -> List[InstanceActionResult]:
    """
    Find GPU instances whose CPUUtilization average over last N minutes is below cpu_threshold.
    """
    ec2, cw = _get_boto3_clients()
    if not ec2 or not cw:
        return []

    instances = list_gpu_instances()
    idle: List[InstanceActionResult] = []

    for inst in instances:
        iid = inst.get("InstanceId")
        itype = inst.get("InstanceType", "?")
        avg_cpu = _avg_cpu_for_instance(cw, iid, minutes=threshold_minutes)
        if avg_cpu < cpu_threshold:
            idle.append(
                InstanceActionResult(
                    instance_id=iid,
                    instance_type=itype,
                    action="candidate-idle",
                    reason=f"Average CPUUtilization {avg_cpu:.2f}% < {cpu_threshold:.2f}% over last {threshold_minutes} minutes",
                )
            )
    return idle

def stop_instances(instance_ids: List[str], dry_run: bool = True) -> List[InstanceActionResult]:
    """
    Stop instances by ID. Dry-run by default.
    """
    settings = get_settings()
    try:
        session = boto3.Session()
        ec2 = session.client("ec2", region_name=settings.aws_region)
    except (NoCredentialsError, PartialCredentialsError):
        return []

    results: List[InstanceActionResult] = []
    if dry_run:
        for iid in instance_ids:
            results.append(
                InstanceActionResult(
                    instance_id=iid,
                    instance_type="?",
                    action="dry-run-stop",
                    reason="Would stop idle GPU instance (dry run)",
                )
            )
        return results

    resp = ec2.stop_instances(InstanceIds=instance_ids)
    for inst in resp.get("StoppingInstances", []):
        results.append(
            InstanceActionResult(
                instance_id=inst.get("InstanceId", "?"),
                instance_type="?",
                action="stop",
                reason="Stopped by AiFinOps idle GPU sweeper",
            )
        )
    return results
