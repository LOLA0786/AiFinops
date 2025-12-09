#!/usr/bin/env python3
"""
Demo: run rightsizing on 3 EC2 instances, generate TF, open PR.
"""
import os
from aifinops.inventory import fetch_ec2_inventory
from aifinops.rightsizing_engine import suggest_rightsize
from aifinops.terraform_pr_ai import generate_tf_from_suggestions

REGION = os.getenv("AWS_DEFAULT_REGION","us-east-1")
REPO = os.getenv("AIFINOPS_REPO","LOLA0786/AiFinops")

def main():
    inv = fetch_ec2_inventory(REGION)
    sample = inv[:3]
    ids = [i["InstanceId"] for i in sample]

    suggestions = [suggest_rightsize(i, REGION) for i in ids]
    text = "\n".join([str(s) for s in suggestions])

    print("Creating PR...")
    out = generate_tf_from_suggestions(
        suggestions=text,
        repo_full=REPO,
        branch="demo-rightsizing-pr",
        title="Demo: Rightsizing Terraform Update",
        push=True
    )
    print(out)

if __name__ == "__main__":
    main()
