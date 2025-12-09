#!/usr/bin/env python3
"""
FastAPI server to handle Slack interactive button approvals.
"""
import json, os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/slack/approve")
async def slack_approve(request: Request):
    body = await request.form()
    payload = json.loads(body.get("payload", "{}"))
    rid = payload.get("actions", [{}])[0].get("value")

    approvals = {}
    if os.path.exists("slack_approvals.json"):
        approvals = json.load(open("slack_approvals.json"))
    approvals[rid] = "approved"
    json.dump(approvals, open("slack_approvals.json","w"), indent=2)

    return JSONResponse({"approved": rid})
