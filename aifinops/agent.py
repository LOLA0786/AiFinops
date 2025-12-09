from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import os
import asyncio

from .aws_cost_fetcher import CostItem
from .config import get_settings
from .llm_clients import LLMClient

@dataclass
class BillExplanation:
    provider_used: Optional[str]
    summary: str
    optimizations: str

async def _call_provider(provider: str, prompt: str, system: Optional[str] = None) -> str:
    client = LLMClient(provider=provider)
    try:
        return await client.chat(prompt, system=system)
    except Exception as e:
        # bubble error for caller to try next provider
        raise

async def explain_bill(cost_items: List[CostItem]) -> BillExplanation:
    """
    Tries LLM providers in order defined by env LLM_FALLBACKS (comma separated).
    Falls back to non-LLM summary if none available.
    """
    if not cost_items:
        return BillExplanation(provider_used=None, summary="No cost data.", optimizations="No suggestions.")

    settings = get_settings()
    fallbacks = os.getenv("LLM_FALLBACKS", "openai,anthropic,xai,gemini").split(",")

    table_lines = [f"{c.date}\t{c.service}\t{c.amount:.4f} {c.unit}" for c in cost_items]
    user_prompt = (
        "You are an aggressive FinOps and cloud cost optimization agent.\n\n"
        "COST TABLE:\n" + "\n".join(table_lines) + "\n\n"
        "Tasks:\n1) Explain the spend.\n2) Highlight anomalies.\n3) Propose concrete optimizations and rough monthly savings.\nReturn two sections: ### Explanation and ### Optimization Suggestions."
    )
    system_prompt = "Be concise and tie each suggestion to estimated savings."

    # Try providers in order
    last_exception = None
    for p in fallbacks:
        p = p.strip()
        if not p:
            continue
        try:
            text = await _call_provider(p, user_prompt, system_prompt)
            # Try split into two parts
            lower = text.lower()
            if "### optimization" in lower:
                idx = lower.index("### optimization")
                summary = text[:idx].strip()
                optimizations = text[idx:].strip()
            else:
                summary = text.strip()
                optimizations = "See explanation above."
            return BillExplanation(provider_used=p, summary=summary, optimizations=optimizations)
        except Exception as e:
            last_exception = e
            continue

    # Fallback non-LLM summary
    total = sum(c.amount for c in cost_items)
    top = sorted(cost_items, key=lambda c: c.amount, reverse=True)[:5]
    lines = [f"Total spend: ${total:.2f}"] + [f"- {c.service}: ${c.amount:.2f}" for c in top]
    return BillExplanation(provider_used=None, summary="\n".join(lines),
                           optimizations="No LLM available; run with LLM_PROVIDER or set LLM_FALLBACKS.")
    
def format_pr_body(cost_items: List[CostItem], explanation: BillExplanation) -> str:
    total = sum(c.amount for c in cost_items)
    top = sorted(cost_items, key=lambda c: c.amount, reverse=True)[:5]
    lines = []
    lines.append("# AiFinOps: Cost Optimization Proposal\n")
    lines.append(f"**Estimated total spend in period:** `${total:.2f}`\n")
    lines.append("## Top services\n")
    for c in top:
        lines.append(f"- **{c.service}**: `${c.amount:.2f}`")
    lines.append("\n## Explanation\n")
    lines.append(explanation.summary)
    lines.append("\n## Optimization Suggestions\n")
    lines.append(explanation.optimizations)
    lines.append(f"\n\n_Provider used: {explanation.provider_used}_")
    return "\n".join(lines)
