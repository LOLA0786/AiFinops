"""
Hybrid AI-Human Loop scaffold

- Voice/Slack approvals
- 'What-if' simulator to estimate cost/throughput tradeoffs
- Co-pilot templates to provide step-by-step change lists

TODO:
- Wire to Slack interactive blocks and optional voice layer (Twilio / Amazon Chime)
- Implement detailed simulator (cost/time/accuracy tradeoffs) using historical metrics
"""

import json
from typing import Dict, Any

def make_what_if_simulation(current_config: Dict[str,Any], change: Dict[str,Any]) -> Dict[str,Any]:
    """
    Simulate a config change (e.g., reduce batch size, change instance type) and estimate cost delta.
    This is a simplistic placeholder; replace with model-based sim later.
    """
    # naive: assume linear cost with instance hours and same performance
    current_cost = current_config.get("hourly_cost", 1.0) * current_config.get("hours", 1.0)
    new_cost = current_cost * change.get("cost_multiplier", 1.0)
    return {"current_cost": current_cost, "new_cost": new_cost, "delta": new_cost - current_cost}

def generate_human_friendly_plan(changes: Dict[str,Any]) -> str:
    """
    Turn change set into a Slack-friendly plan (bullets + risk + revert steps)
    """
    lines = []
    lines.append("*Proposed Changes*")
    for k,v in changes.items():
        lines.append(f"- {k}: {v}")
    lines.append("\\n*Risk*: low. Revert: run 'aifinops revert <id>'")
    return "\\n".join(lines)
