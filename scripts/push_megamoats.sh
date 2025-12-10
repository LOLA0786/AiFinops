#!/bin/bash
set -euo pipefail
BRANCH="${BRANCH_NAME:-megamoats-v2-implementation}"
git checkout -B "$BRANCH"
git add -A
git commit -m "Add MegaMoats v1..v10 scaffold" || echo "Nothing to commit"
git push -u origin "$BRANCH"
if command -v gh >/dev/null 2>&1; then
  gh pr create --base main --head "$BRANCH" --title "MegaMoats v1..v10 scaffold" --body "Scaffold for moats v1..v10"
else
  echo "gh CLI not installed."
fi
