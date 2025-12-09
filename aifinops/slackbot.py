from __future__ import annotations
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def post_message(channel: str, text: str) -> dict:
    token = os.getenv("SLACK_TOKEN")
    if not token:
        return {"error":"no slack token configured"}
    client = WebClient(token=token)
    try:
        resp = client.chat_postMessage(channel=channel, text=text)
        return dict(resp)
    except SlackApiError as e:
        return {"error": str(e)}
