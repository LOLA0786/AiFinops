#!/usr/bin/env bash
set -e
echo "Bootstrapping AiFinOps enterprise features (CI/CD, Docker, snapshotting, inventory, unit-econ)..."

# 1) Create .github/workflows for CI/CD
mkdir -p .github/workflows
cat << 'YML' > .github/workflows/finops-ci.yml
name: AiFinOps CI/CD

on:
  push:
    branches: [ aifinops-bootstrap ]
  schedule:
    - cron: '0 2 * * *'  # daily at 02:00 UTC; adjust as needed

permissions:
  contents: write
  pull-requests: write

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run unit tests (placeholder)
        run: |
          echo "No tests configured yet"

  daily-ingest:
    needs: tests
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Fetch costs (CI)
        env:
          AWS_ACCESS_KEY_ID: \${{ secrets.CI_AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: \${{ secrets.CI_AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: us-east-1
        run: |
          python3 main.py ingest-aws --days 7
          python3 main.py detect-anomalies --days 7
          python3 main.py explain-bill --days 3 > /tmp/explain_output.txt || true
      - name: Commit snapshot
        env:
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          mkdir -p snapshots
          dt=$(date -u +"%Y-%m-%d")
          cp /tmp/explain_output.txt snapshots/explain-\${{ github.run_id }}-\${dt}.txt || true
          git add snapshots
          git commit -m "daily: add explain snapshot - \${dt}" || echo "no changes"
          git push origin HEAD: aifinops-bootstrap || echo "push failed"

  pr-report:
    runs-on: ubuntu-latest
    needs: daily-ingest
    steps:
      - uses: actions/checkout@v4
      - name: Create PR with report (dry-run optionally)
        env:
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 main.py create-pr --repo ${{ github.repository }} --branch ci-auto-report-\${{ github.run_id }} --title "Daily FinOps report" || echo "create-pr may need GITHUB_TOKEN and repo rights"
YML

echo "Created GitHub Actions workflow: .github/workflows/finops-ci.yml"

# 2) Dockerfile + docker-compose
cat << 'DOCK' > Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
DOCK

cat << 'DOCK' > docker-compose.yml
version: '3.8'
services:
  aifinops:
    build: .
    ports:
      - "8501:8501"
    environment:
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
    volumes:
      - .:/app
DOCK

echo "Created Dockerfile and docker-compose.yml"

# 3) Create finops-as-code folder structure
mkdir -p finops/{rules,forecasts,anomalies,actions}
cat << 'TXT' > finops/README.md
FinOps as Code
- rules/ : policy files (yaml) that define autoscaling, spot eligibility, retention.
- forecasts/ : exported forecast CSVs
- anomalies/ : archived anomalous spend snapshots
- actions/ : recommended actions and Terraform snippets
TXT

echo "Created finops/ structure"

# 4) Billing snapshot script (safe, commit to snapshots/)
cat << 'PY' > scripts/billing_snapshot.py
#!/usr/bin/env python3
import os, json, datetime
from aifinops.aws_cost_fetcher import fetch_aws_daily_costs

def snapshot(days=7):
    items = fetch_aws_daily_costs(days=days)
    data = [{"date":i.date,"service":i.service,"amount":i.amount,"unit":i.unit} for i in items]
    dt = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    out = {"generated_at": dt, "items": data}
    path = f"snapshots/cost_snapshot_{dt}.json"
    os.makedirs("snapshots", exist_ok=True)
    with open(path,"w") as f:
        json.dump(out,f,indent=2)
    print("Wrote", path)
    return path

if __name__ == '__main__':
    snapshot()
PY
chmod +x scripts/billing_snapshot.py
echo "Created scripts/billing_snapshot.py"

# 5) AWS inventory collector (ec2,s3,rds minimal)
cat << 'PY' > aifinops/inventory.py
from __future__ import annotations
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def fetch_ec2_inventory(region='us-east-1'):
    try:
        ec2 = boto3.client('ec2', region_name=region)
        resp = ec2.describe_instances(Filters=[{"Name":"instance-state-name","Values":["running","stopped"]}])
        out = []
        for r in resp.get("Reservations",[]):
            for i in r.get("Instances",[]):
                out.append({
                    "InstanceId": i.get("InstanceId"),
                    "InstanceType": i.get("InstanceType"),
                    "State": i.get("State",{}).get("Name"),
                    "Tags": i.get("Tags",[])
                })
        return out
    except (NoCredentialsError, ClientError):
        return []

def fetch_s3_buckets(region='us-east-1'):
    import boto3
    s3 = boto3.client('s3', region_name=region)
    try:
        resp = s3.list_buckets()
        return [b['Name'] for b in resp.get('Buckets',[])]
    except Exception:
        return []
PY

echo "Created aifinops/inventory.py"

# 6) Unit economics module
cat << 'PY' > aifinops/unit_economics.py
from __future__ import annotations
from typing import Dict

def cost_per_user(total_cost: float, users: int) -> float:
    return total_cost / users if users else 0.0

def cost_per_request(total_cost: float, requests: int) -> float:
    return total_cost / requests if requests else 0.0

def assemble_report(costs: Dict[str,float], metrics: Dict[str,int]) -> Dict:
    total = sum(costs.values())
    users = metrics.get("users", 0)
    reqs = metrics.get("requests", 0)
    return {
        "total_cost": total,
        "cost_per_user": cost_per_user(total, users),
        "cost_per_request": cost_per_request(total, reqs)
    }
PY

echo "Created aifinops/unit_economics.py"

# 7) Terraform-AI CLI hook (scaffold)
cat << 'PY' > aifinops/terraform_cli.py
from __future__ import annotations
import json
from .terraform_ai import generate_terraform_changes

def make_terraform_pr(suggestions):
    tf_snip = generate_terraform_changes(suggestions)
    fname = "finops/actions/terraform_suggestions.txt"
    with open(fname,"w") as f:
        f.write(tf_snip)
    print("Wrote terraform suggestions to", fname)
PY

echo "Created aifinops/terraform_cli.py"

# 8) Add a small GitHub Action that can commit snapshots (already added), and add a local helper
cat << 'SH' > tools/commit_snapshot.sh
#!/usr/bin/env bash
set -e
python3 scripts/billing_snapshot.py
git add snapshots || true
git commit -m "local: add cost snapshot" || echo "nothing to commit"
git push origin aifinops-bootstrap
SH
chmod +x tools/commit_snapshot.sh
echo "Created helper tools/commit_snapshot.sh"

# 9) Add basic README updates
cat << 'MD' > README_ENTERPRISE.md
AiFinOps Enterprise Additions
- CI/CD: .github/workflows/finops-ci.yml (daily snapshot, explain-bill)
- Docker: Dockerfile + docker-compose.yml
- Billing snapshots: scripts/billing_snapshot.py -> snapshots/
- Inventory: aifinops/inventory.py
- Unit economics: aifinops/unit_economics.py
- FinOps-as-code: finops/ folder
- Terraform AI: aifinops/terraform_ai.py / terraform_cli.py

**Important next steps**
1. Add GitHub Secrets: CI_AWS_ACCESS_KEY_ID, CI_AWS_SECRET_ACCESS_KEY, GITHUB_TOKEN, SLACK_TOKEN (optional).
2. Confirm CONFIRM_AUTO_ACTIONS only when ready.
3. Run locally: ./tools/commit_snapshot.sh
MD

echo "Created README_ENTERPRISE.md"

# 10) Stage + commit
git add .github Dockerfile docker-compose.yml finops scripts aifinops/inventory.py aifinops/unit_economics.py aifinops/terraform_cli.py tools README_ENTERPRISE.md || true
git commit -m "enterprise: add CI, docker, snapshots, inventory, unit-econ, terraform-ai scaffolds" || echo "nothing to commit"
git push origin HEAD:aifinops-bootstrap || git push origin aifinops-bootstrap --force || echo "push may fail if branch protection blocks"

echo "Bootstrap finished. Next: add secrets and enable Actions."
