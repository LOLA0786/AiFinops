from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List

from .config import get_settings
from .aws_cost_fetcher import CostItem
from .llm_clients import LLMClient

@dataclass
class BillExplanation:
    summary: str
    suggestions: str

async def explain_bill(cost_items: List[CostItem]) -> BillExplanation:
    """V2/V3 – feed cost table into LLM and get explanations + suggestions."""
    settings = get_settings()
    provider = settings.llm_config.provider if settings.llm_config else None
    if not provider:
        # Fallback: non-LLM explanation
        total = sum(c.amount for c in cost_items)
        top = sorted(cost_items, key=lambda c: c.amount, reverse=True)[:5]
        lines = [f"Total last days: ${total:.2f}"] + [
            f"- {c.date} / {c.service}: ${c.amount:.2f} {c.unit}" for c in top
        ]
        return BillExplanation(
            summary="\n".join(lines),
            suggestions="Set LLM_PROVIDER to get richer advice (xai/openai/gemini/anthropic).",
        )

    client = LLMClient(provider=provider)  # type: ignore[arg-type]

    table_lines = [
        f"{c.date}\t{c.service}\t{c.amount:.4f} {c.unit}" for c in cost_items
    ]
    prompt = (
        "You are an aggressive FinOps agent. Given this AWS cost breakdown (date, service, amount, unit), "
        "1) explain in plain English what changed and why, 2) highlight anomalies / spikes, "
        "3) propose concrete cost-saving actions (rightsizing, kill idle, switch instance family, etc.).\n\n"
        "COST TABLE:\n" + "\n".join(table_lines)
    )

    system = "Be ruthless about waste. Tie every suggestion to an estimated monthly savings."
    text = await client.chat(prompt, system=system)

    return BillExplanation(summary=text, suggestions="Included above.")
