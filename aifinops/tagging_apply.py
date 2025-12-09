from __future__ import annotations
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from typing import List, Dict

def apply_tags_ec2(instance_ids: List[str], tags: Dict[str, str], region: str = "us-east-1", dry_run: bool = True) -> Dict[str, object]:
    """
    Apply tags to EC2 instances.
    - dry_run True -> returns planned changes
    - To actually apply: set CONFIRM_AUTO_ACTIONS=true in .env and call with dry_run=False
    """
    confirm = os.getenv("CONFIRM_AUTO_ACTIONS", "false").lower() in ("1","true","yes")
    if not confirm and not dry_run:
        raise PermissionError("Auto actions not allowed. Set CONFIRM_AUTO_ACTIONS=true to permit apply.")

    if not instance_ids:
        return {"status": "no_instances", "applied": []}

    tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]

    if dry_run:
        return {"status": "dry_run", "planned": {"instance_ids": instance_ids, "tags": tags}}

    try:
        ec2 = boto3.client("ec2", region_name=region)
        resp = ec2.create_tags(Resources=instance_ids, Tags=tag_list)
        return {"status": "success", "response": str(resp)}
    except NoCredentialsError:
        return {"status": "no_credentials", "message": "AWS credentials not found."}
    except ClientError as e:
        return {"status": "client_error", "message": str(e)}
