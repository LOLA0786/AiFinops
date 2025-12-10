#!/bin/bash
set -e

BRANCH="aifinops-megamoats"

git checkout -B "$BRANCH"
git add megamoots k8s scripts
git commit -m "Add MegaMoats scaffolding v1..v5" || true
git push -u origin "$BRANCH"

if command -v gh >/dev/null 2>&1; then
    gh pr create --base main --head "$BRANCH" \
      --title "Add MegaMoats scaffolding" \
      --body "Scaffolding for GPU Telemetry, Oracle, Cluster DNA, Training Analyzer, and Autonomous Router"
else
    echo "gh CLI not installed or authenticated"
fi
