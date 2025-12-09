#!/bin/bash
set -e

echo "=== SWITCHING TO aifinops-bootstrap BRANCH ==="
git checkout -B aifinops-bootstrap

echo "=== ADDING ALL FILES ==="
git add .

echo "=== COMMITTING ==="
git commit -m "Add workflows, GPU monitoring, reports, and enterprise automation" || echo "Nothing to commit."

echo "=== PUSHING TO REMOTE ==="
git push origin aifinops-bootstrap

echo "=== CREATING PULL REQUEST ==="
if gh auth status >/dev/null 2>&1; then
  gh pr create \
    --base main \
    --head aifinops-bootstrap \
    --title "Enterprise Automation + GPU Monitoring + Reports" \
    --body "Adds auto-merge, model training, monthly reporting, GPU monitoring agents, and bootstrap workflows."
else
  echo "GitHub CLI not authenticated. Run: gh auth login"
fi

echo "=== DONE — CHECK GITHUB FOR NEW PR ==="
