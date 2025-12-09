from __future__ import annotations
from typing import List, Dict
from .llm_clients import LLMClient
import os

def generate_terraform_changes(suggestions: List[Dict], provider: str = None) -> str:
    """
    Generate Terraform snippets that implement rightsizing / tagging / reservation changes.
    This uses LLM to produce terraform code. Real pipeline must add plan/apply & review.
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    client = LLMClient(provider=provider)
    prompt = "Generate terraform snippets to implement these changes:\\n" + str(suggestions)
    try:
        resp = client.chat(prompt)
    except Exception as e:
        return "LLM not available: " + str(e)
    return resp
