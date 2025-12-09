#!/usr/bin/env python3
"""
Three-step hypermode apply workflow:
1) Dry-run idle instance detection
2) Slack approval request
3) Stop instances after approval
"""

import os, time, json, uuid
from aifinops.terminate_workflow import post_approval_request, stop_instances_safe
from aifinops.rightsizing_engine import suggest_rightsize
from aifinops.inventory import fetch_ec2_inventory

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
REQUEST_ID = str(uuid.uuid4())[:8]

def find_idle_instances(limit=3):
    inventory = fetch_ec2_inventory(REGION)
    candidates = []
    for inst in inventory:
        iid = inst.get("InstanceId")
        if not iid: continue
        sug = suggest_rightsize(iid, REGION)
        if sug.get("p90", 100) < 10:
            candidates.append(iid)
        if len(candidates) >= limit:
            break
    return candidates

def main():
    print("=== STEP 1: DRY RUN ===")
    candidates = find_idle_instances()
    print("Idle:", candidates)

    print("=== STEP 2: Slack Approval ===")
    payload = post_approval_request(
        [{"InstanceId": iid} for iid in candidates],
        request_id=REQUEST_ID
    )
    print(payload)
    print(f"Tell Slack: APPROVE {REQUEST_ID}")

    print("Waiting for approval via slack_approvals.json")
    while True:
        if os.path.exists("slack_approvals.json"):
            approvals = json.load(open("slack_approvals.json"))
            if approvals.get(REQUEST_ID) == "approved":
                break
        time.sleep(5)

    print("=== STEP 3: APPLY ===")
    resp = stop_instances_safe(candidates, dry_run=False, region=REGION)
    print(resp)

if __name__ == "__main__":
    main()
