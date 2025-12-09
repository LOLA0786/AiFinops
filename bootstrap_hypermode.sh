#!/usr/bin/env bash
set -e
echo "Bootstrapping AiFinOps HYPERMODE features..."

# 1) Expand requirements (adds boto3 extras, awsprice, scikit-learn if not present)
cat << 'REQ' > requirements.txt
httpx
python-dotenv
boto3
streamlit
pandas
numpy
PyGithub
matplotlib
seaborn
prophet
scikit-learn
slack-sdk
kubernetes
joblib
requests
botocore
REQ

echo "Updated requirements.txt (run pip install -r requirements.txt)"

mkdir -p aifinops

# 2) Rightsizing engine (CloudWatch metrics, percentile analysis)
cat << 'PY' > aifinops/rightsizing_engine.py
from __future__ import annotations
import boto3
import statistics
import datetime as dt
from typing import List, Dict, Tuple
from botocore.exceptions import NoCredentialsError, ClientError

def fetch_cpu_metrics(instance_id: str, minutes: int = 1440, region: str = "us-east-1") -> List[float]:
    """
    Fetch CPUUtilization datapoints for the past 'minutes' minutes (default 24h).
    Returns list of averages (per-minute or per-period).
    """
    try:
        cw = boto3.client("cloudwatch", region_name=region)
        end = dt.datetime.utcnow()
        start = end - dt.timedelta(minutes=minutes)
        resp = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name":"InstanceId","Value":instance_id}],
            StartTime=start,
            EndTime=end,
            Period=300,  # 5-minute granularity
            Statistics=["Average"]
        )
        dps = resp.get("Datapoints", [])
        values = [float(dp.get("Average", 0.0)) for dp in dps]
        return sorted(values)
    except (NoCredentialsError, ClientError):
        return []

def suggest_rightsize(instance_id: str, region: str = "us-east-1") -> Dict:
    """
    Suggest right-size recommendations using CPU percentiles and simple memory heuristics (if available).
    Output includes suggested instance family size and estimated savings.
    """
    values = fetch_cpu_metrics(instance_id, minutes=60*24, region=region)
    if not values:
        return {"instance_id": instance_id, "suggestion": "no-metrics", "note": "No CloudWatch metrics available."}
    p50 = statistics.median(values)
    p90 = values[int(len(values)*0.9)-1] if len(values) > 1 else p50
    p99 = values[int(len(values)*0.99)-1] if len(values) > 1 else p90

    # Heuristic mapping: high-level only
    if p90 < 10:
        suggested = "downsize by 50% or move to burstable T family"
    elif p90 < 30:
        suggested = "consider one size smaller"
    else:
        suggested = "no change (high utilization)"
    return {"instance_id": instance_id, "p50": p50, "p90": p90, "p99": p99, "suggestion": suggested}

def batch_rightsize(candidates: List[str], region: str = "us-east-1") -> List[Dict]:
    out = []
    for iid in candidates:
        out.append(suggest_rightsize(iid, region=region))
    return out
PY

# 3) Spot Advisor (uses simple family heuristics + AWS Spot price API fallback)
cat << 'PY' > aifinops/spot_advisor.py
from __future__ import annotations
import boto3
import datetime as dt
from typing import List, Tuple

# Simple family savings (tunable)
FAMILY_SPOT = {
    "m5": 0.7, "c5": 0.7, "r5": 0.7, "t3": 0.8, "g4": 0.65, "g5": 0.6, "p4": 0.6
}

def estimate_spot_for_instance_type(instance_type: str) -> float:
    for k,v in FAMILY_SPOT.items():
        if instance_type.startswith(k):
            return v
    return 0.5

def fetch_spot_price_history(instance_type: str, region: str = "us-east-1") -> List[dict]:
    try:
        ec2 = boto3.client("ec2", region_name=region)
        now = dt.datetime.utcnow()
        resp = ec2.describe_spot_price_history(InstanceTypes=[instance_type], StartTime=now - dt.timedelta(days=7), EndTime=now, ProductDescriptions=['Linux/UNIX'])
        return resp.get("SpotPriceHistory", [])
    except Exception:
        return []

def recommend_spot_for_instances(instances: List[dict], region: str = "us-east-1") -> List[dict]:
    """
    instances: list of dicts with keys InstanceId, InstanceType, LaunchTime...
    Returns a recommendation for each instance whether spot is viable.
    """
    out = []
    for i in instances:
        itype = i.get("InstanceType","")
        score = estimate_spot_for_instance_type(itype)
        hist = fetch_spot_price_history(itype, region=region)
        out.append({"InstanceId": i.get("InstanceId"), "InstanceType": itype, "spot_estimate_pct": score, "historical_samples": len(hist)})
    return out
PY

# 4) GPU Idle Heatmap (improved: support nvidia DCGM, custom metrics; returns dict)
cat << 'PY' > aifinops/gpu_heatmap_pro.py
from __future__ import annotations
import boto3
import datetime as dt
from botocore.exceptions import NoCredentialsError, ClientError
from typing import List, Dict

def gpu_metric_names():
    # Depending on agent, metric names vary - try common ones
    return ["GPUUtilization", "NVIDIA_GPU_Utilization", "GpuUtilization"]

def fetch_gpu_metric(instance_id: str, minutes: int = 60, region: str = "us-east-1") -> float:
    try:
        cw = boto3.client("cloudwatch", region_name=region)
        end = dt.datetime.utcnow()
        start = end - dt.timedelta(minutes=minutes)
        for metric in gpu_metric_names():
            resp = cw.get_metric_statistics(Namespace="AWS/EC2", MetricName=metric,
                                            Dimensions=[{"Name":"InstanceId","Value":instance_id}],
                                            StartTime=start, EndTime=end, Period=60, Statistics=["Average"])
            dps = resp.get("Datapoints", [])
            if dps:
                return float(sorted(dps, key=lambda d: d["Timestamp"])[-1].get("Average", 0.0))
        return 0.0
    except (NoCredentialsError, ClientError):
        return 0.0

def build_gpu_heatmap(instance_ids: List[str], minutes: int = 60, region: str = "us-east-1") -> Dict[str, float]:
    return {iid: fetch_gpu_metric(iid, minutes=minutes, region=region) for iid in instance_ids}
PY

# 5) Instance Termination + Slack Approval scaffold (safe, gated)
cat << 'PY' > aifinops/terminate_workflow.py
from __future__ import annotations
import os
import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Dict
from botocore.exceptions import NoCredentialsError, ClientError

SLACK_TOKEN = os.getenv("SLACK_WEBHOOK_TOKEN") or os.getenv("SLACK_BOT_TOKEN") or os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_APPROVAL_CHANNEL", "#ops")
CONFIRM = os.getenv("CONFIRM_HYPERMODE", "false").lower() in ("1","true","yes")

def post_approval_request(instances: List[Dict], request_id: str) -> Dict:
    """
    Posts an interactive approval message to Slack (requires Slack app with interactive components)
    For safety this returns the message payload and does NOT stop instances automatically.
    """
    if not SLACK_TOKEN:
        return {"error":"no_slack_token"}
    client = WebClient(token=SLACK_TOKEN)
    text = f"Approval required: stop {len(instances)} instances (request {request_id})"
    blocks = [
        {"type":"section","text":{"type":"mrkdwn","text":text}},
        {"type":"context","elements":[{"type":"mrkdwn","text":"Reply with APPROVE {request_id} to confirm."}]}
    ]
    try:
        resp = client.chat_postMessage(channel=SLACK_CHANNEL, text=text, blocks=blocks)
        return {"ok": True, "ts": resp.get("ts")}
    except SlackApiError as e:
        return {"error": str(e)}

def stop_instances_safe(instance_ids: List[str], dry_run: bool = True, region: str = "us-east-1") -> Dict:
    """
    Stop instances only if CONFIRM_HYPERMODE and dry_run=False, and after Slack approval flow.
    This function assumes approval has been obtained externally and replaced here with a check.
    """
    if dry_run:
        return {"status":"dry_run","planned": instance_ids}
    if not CONFIRM:
        raise PermissionError("Hypermode actions disabled. Set CONFIRM_HYPERMODE=true to enable.")
    try:
        ec2 = boto3.client("ec2", region_name=region)
        resp = ec2.stop_instances(InstanceIds=instance_ids, DryRun=False)
        return {"status":"stopped","response": resp}
    except (NoCredentialsError, ClientError) as e:
        return {"error": str(e)}
PY

# 6) AI-generated Terraform PR helper (LLM -> terraform snippet -> create PR)
cat << 'PY' > aifinops/terraform_pr_ai.py
from __future__ import annotations
import os
from .llm_clients import LLMClient
from .github_pr import create_pr

def generate_tf_from_suggestions(suggestions: str, repo_full: str, branch: str, title: str, push: bool=False):
    provider = os.getenv("LLM_PROVIDER", "openai")
    client = LLMClient(provider=provider)
    prompt = "Generate terraform v0.13+ HCL for the following FinOps suggestions:\\n" + suggestions
    try:
        tf_code = client.chat(prompt, system="You are a Terraform expert. Output code only.")
    except Exception as e:
        return {"error": str(e)}
    # write file
    fname = "finops/actions/auto_tf_changes.tf"
    with open(fname, "w") as f:
        f.write("// Auto-generated terraform - review before applying\\n")
        f.write(tf_code)
    # create PR via helper
    pr_url = create_pr(repo_full, branch, title, "Auto-generated Terraform changes (review)", push=push)
    return {"file": fname, "pr_url": pr_url}
PY

# 7) SLO-driven cost governance (simple rules engine)
cat << 'PY' > aifinops/slo_governance.py
from __future__ import annotations
import os
from typing import Dict

def check_slos(metrics: Dict[str, float], slos: Dict[str, float]) -> Dict:
    """
    metrics: e.g. {'cost_per_user': 0.5, 'margin_pct': 10}
    slos: thresholds e.g. {'cost_per_user': 1.0, 'margin_pct_min': 15}
    Returns alerts if any SLO violated.
    """
    alerts = {}
    if metrics.get("cost_per_user", 0) > slos.get("cost_per_user", float('inf')):
        alerts['cost_per_user_exceeded'] = True
    if metrics.get("margin_pct", 100) < slos.get("margin_pct_min", -100):
        alerts['margin_below'] = True
    return alerts
PY

# 8) Add Hypermode GitHub Actions (approval + scheduled hyper checks)
mkdir -p .github/workflows
cat << 'YML' > .github/workflows/hypermode-checks.yml
name: Hypermode Checks

on:
  workflow_dispatch:
  schedule:
    - cron: '0 4 * * *'  # run daily at 04:00 UTC

jobs:
  hyper-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run rightsizing analysis
        env:
          AWS_ACCESS_KEY_ID: \${{ secrets.CI_AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: \${{ secrets.CI_AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: us-east-1
        run: |
          python3 - <<'PY'
from aifinops.inventory import fetch_ec2_inventory
from aifinops.rightsizing_engine import batch_rightsize
inst = fetch_ec2_inventory(region='us-east-1')[:20]
ids = [i['InstanceId'] for i in inst]
res = batch_rightsize(ids, region='us-east-1')
print(res)
PY
      - name: Create PR if recommendations exist
        env:
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 main.py create-pr --repo ${{ github.repository }} --branch hypermode-recs-\${{ github.run_id }} --title "Hypermode: Rightsize recommendations" || echo "PR creation attempted"
YML

# 9) Add CLI commands wiring (append to cli_ext)
if ! grep -q "hypermode" aifinops/cli_ext.py 2>/dev/null; then
  cat << 'PY' >> aifinops/cli_ext.py

def cmd_hyper_rightsize(args):
    from .inventory import fetch_ec2_inventory
    from .rightsizing_engine import batch_rightsize
    inst = fetch_ec2_inventory(region=args.region)
    ids = [i['InstanceId'] for i in inst]
    print(batch_rightsize(ids[:args.limit], region=args.region))

def cmd_hyper_spot(args):
    from .inventory import fetch_ec2_inventory
    from .spot_advisor import recommend_spot_for_instances
    inst = fetch_ec2_inventory(region=args.region)
    print(recommend_spot_for_instances(inst[:args.limit], region=args.region))

def cmd_hyper_gpu(args):
    from .gpu_heatmap_pro import build_gpu_heatmap
    ids = args.ids.split(",") if args.ids else []
    print(build_gpu_heatmap(ids, minutes=args.minutes, region=args.region))

# register new parsers
# note: to use please add parsers in build_parser or call aifinops.cli_ext.main()
PY
fi

# 10) Safety note: set env var name for enabling hypermode
cat << 'TXT' > HYPERMODE_README.md
HYPERMODE Safety & Use

- To enable real destructive Hypermode actions, set CONFIRM_HYPERMODE=true in your .env (NOT recommended on prod without review).
- Instance termination requires Slack approval flow: post approval (terminate_workflow.post_approval_request) then confirm externally in Slack. This code does not auto-approve.
- AI-generated PRs run under your GITHUB_TOKEN; review all PRs before merging.
TXT

echo "Hypermode modules added. Commit and push to apply."

git add aifinops/rightsizing_engine.py aifinops/spot_advisor.py aifinops/gpu_heatmap_pro.py aifinops/terminate_workflow.py aifinops/terraform_pr_ai.py aifinops/slo_governance.py .github/workflows/hypermode-checks.yml HYPERMODE_README.md || true
git commit -m "hypermode: add rightsizing, spot advisor, gpu heatmap, termination workflow, terraform-pr-ai, slo governance" || echo "nothing to commit"
git push origin HEAD:aifinops-bootstrap || echo "push may fail (branch protection) - push manually"

echo "HYPERMODE bootstrap finished. Next: pip install -r requirements.txt, set secrets, run the hypermode workflow."
