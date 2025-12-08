from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .config import get_settings
from .llm_clients import LLMClient

@dataclass
class PromptVariant:
    original: str
    optimized: str
    estimated_token_savings: float
    notes: str

async def optimize_prompt(original_prompt: str) -> PromptVariant:
    """V5 – have LLM rewrite a prompt to be cheaper while preserving intent."""
    settings = get_settings()
    provider = settings.llm_config.provider if settings.llm_config else None
    if not provider:
        return PromptVariant(
            original=original_prompt,
            optimized=original_prompt,
            estimated_token_savings=0.0,
            notes="Set LLM_PROVIDER to xai/openai/gemini/anthropic to enable optimization.",
        )

    client = LLMClient(provider=provider)  # type: ignore[arg-type]

    sys = (
        "You are a prompt compression expert. Rewrite prompts to use fewer tokens while "
        "keeping behavior the same. Avoid verbosity, remove repetition, keep structure."
    )
    user = (
        "Rewrite this prompt to be 40% shorter BUT functionally equivalent. Then estimate token savings "
        "as a percentage. Respond in JSON with keys: optimized, savings_pct. Prompt:\n\n"
        + original_prompt
    )
    raw = await client.chat(user, system=sys)

    import json

    try:
        data = json.loads(raw)
        optimized = data.get("optimized", original_prompt)
        savings_pct = float(data.get("savings_pct", 0))
    except Exception:
        optimized = original_prompt
        savings_pct = 0.0

    return PromptVariant(
        original=original_prompt,
        optimized=optimized,
        estimated_token_savings=savings_pct,
        notes="LLM estimated savings_pct as token reduction percentage.",
    )
