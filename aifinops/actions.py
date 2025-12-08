from __future__ import annotations

from dataclasses import dataclass
from typing import List

import boto3

from .config import get_settings

@dataclass
class InstanceActionResult:
    instance_id: str
    action: str
    reason: str

def find_idle_gpus(threshold_minutes: int = 30) -> List[str]:
    """V4 – stub: here you'd inspect CloudWatch metrics to find idle GPU instances.

    For now, this just returns an empty list. You can fill it later.
    """
    # TODO: Implement using CloudWatch metrics (GPUUtilization, CPUUtilization, etc.)
    return []

def stop_instances(instance_ids: List[str], dry_run: bool = True) -> List[InstanceActionResult]:
    if not instance_ids:
        return []
    settings = get_settings()
    session_kwargs = {}
    if settings.aws_profile:
        session_kwargs["profile_name"] = settings.aws_profile
    session = boto3.Session(**session_kwargs)
    ec2 = session.client("ec2", region_name=settings.aws_region)

    results: List[InstanceActionResult] = []
    if dry_run:
        for iid in instance_ids:
            results.append(
                InstanceActionResult(
                    instance_id=iid,
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
                action="stop",
                reason="Stopped by AiFinOps idle GPU sweeper",
            )
        )
    return results
