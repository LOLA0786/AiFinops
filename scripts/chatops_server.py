#!/usr/bin/env python3
"""
ChatOps FastAPI server for Slack slash commands.

Flow:
- Slack sends POST to /slash with command text (e.g. "/finops optimize --days 3")
- This server validates the Slack token (if provided), builds a repository_dispatch payload
  and calls GitHub REST API to trigger the ChatOps workflow (repository_dispatch event).
- GitHub Actions listens for repository_dispatch (event_type: chatops) and runs the requested command.

REQUIREMENTS:
- Export GITHUB_TOKEN (PAT) with 'repo' scope or set in .env
- If using Slack verification, set SLACK_VERIFICATION_TOKEN or SLACK_SIGNING_SECRET
"""

import os
import json
import requests
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # needs repo:status, repo scope for dispatch
REPO = os.getenv("AIFINOPS_REPO", "LOLA0786/AiFinops")
# Optional Slack token verification (set SLACK_VERIFICATION_TOKEN or SLACK_SIGNING_SECRET)
SLACK_VERIFICATION_TOKEN = os.getenv("SLACK_VERIFICATION_TOKEN")

GITHUB_API = "https://api.github.com"

def trigger_repository_dispatch(event_type: str, client_payload: dict):
    """
    Calls GitHub repository dispatch API to trigger workflows.
    """
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not set in env")
    url = f"{GITHUB_API}/repos/{REPO}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    payload = {
        "event_type": event_type,
        "client_payload": client_payload
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code not in (204, 201):
        raise RuntimeError(f"GitHub dispatch failed: {resp.status_code} {resp.text}")
    return True

@app.post("/slash")
async def slack_slash(command: str = Form(...), token: str = Form(None), user_name: str = Form(None)):
    """
    Slack posts here with form-encoded fields including 'command' and 'text'.
    We accept 'command' arg or 'text' depending on how Slack is configured.
    For safety, we only accept commands that start with known verbs: optimize, kill-idle, forecast, create-pr
    Example command text: "optimize --days 7"
    """
    text = command if command else ""
    if token and SLACK_VERIFICATION_TOKEN and token != SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Slack token")

    # Slack may send the actual user text in 'text' form field, but we'll use "command" for generic form.
    # If the incoming form uses 'text', adjust accordingly.
    # For simplicity, allow the entire request body to be used as `text` when present.
    if not text:
        body = await Request.form.__call__(Request)  # fallback (rare)
        text = body.get("text") or ""

    text = text.strip()
    if not text:
        return JSONResponse({"ok": False, "message": "No command text provided. Usage: /finops <action> [--flags]"}, status_code=400)

    # Parse safe verb (first token)
    parts = text.split()
    verb = parts[0].lower()
    allowed = {"optimize", "kill-idle", "forecast", "create-pr", "explain-bill", "simulate", "detect-anomalies", "analyze-util"}
    if verb not in allowed:
        return JSONResponse({"ok": False, "message": f"Unsupported action: {verb}. Allowed: {sorted(list(allowed))}"}, status_code=400)

    # Build payload that will be forwarded to GitHub Actions
    payload = {
        "action": verb,
        "args": parts[1:],
        "requested_by": user_name or "slack_user",
    }

    try:
        trigger_repository_dispatch("chatops", payload)
    except Exception as e:
        return JSONResponse({"ok": False, "message": f"Failed to trigger action: {e}"}, status_code=500)

    return JSONResponse({"ok": True, "message": f"Triggered {verb}. Check Actions for results."})
