from __future__ import annotations
from typing import List, Dict
from .llm_clients import LLMClient
import os

def suggest_tags_for_resources(resources: List[Dict[str, str]], provider: str = None) -> str:
    """
    resources: list of { 'id': 'i-...', 'name': 'svc-name', 'type': 'ec2' }
    returns textual recommendations (LLM)
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    client = LLMClient(provider=provider)
    # Build prompt
    lines = ["We have the following cloud resources. Suggest tag keys and values to allocate cost and reasons:"]
    for r in resources:
        lines.append(f"- id: {r.get('id')} type: {r.get('type')} name: {r.get('name')}")
    prompt = "\\n".join(lines)
    try:
        text = client.chat(prompt, system="You are a cloud tagging expert. Provide JSON with tags per resource.")
    except Exception as e:
        return "LLM not available: " + str(e)
    return text

def generate_terraform_tag_snippets(resources: List[Dict[str, str]]) -> str:
    """
    Simple terraform aws_tagging snippets for EC2. (Advisory; not applied)
    """
    lines = []
    for r in resources:
        if r.get("type","").lower() == "ec2":
            lines.append(f'resource "aws_instance" "{r["id"]}" {{')
            lines.append(f'  instance_id = "{r["id"]}"')
            lines.append('  tags = {')
            lines.append('    "team" = "REPLACE_TEAM"')
            lines.append('    "cost_center" = "REPLACE_CC"')
            lines.append('  }')
            lines.append('}')
            lines.append('')
    return "\\n".join(lines)
