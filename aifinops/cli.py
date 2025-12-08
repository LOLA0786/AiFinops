from __future__ import annotations

import argparse
import asyncio
from textwrap import dedent

from .aws_cost_fetcher import fetch_aws_daily_costs
from .agent import explain_bill
from .actions import find_idle_gpus, stop_instances
from .prompt_optimizer import optimize_prompt

def cmd_ingest(args: argparse.Namespace) -> None:
    items = fetch_aws_daily_costs(days=args.days)
    print(f"Fetched {len(items)} cost rows for last {args.days} days.\n")
    for c in items:
        print(f"{c.date} | {c.service:<40} | ${c.amount:.4f} {c.unit}")

def cmd_explain(args: argparse.Namespace) -> None:
    items = fetch_aws_daily_costs(days=args.days)

    async def run():
        res = await explain_bill(items)
        print("=== BILL EXPLANATION ===\n")
        print(res.summary)
        print("\n=== SUGGESTIONS ===\n")
        print(res.suggestions)

    asyncio.run(run())

def cmd_sweep_gpus(args: argparse.Namespace) -> None:
    idle = find_idle_gpus(threshold_minutes=args.threshold)
    if not idle:
        print("No idle GPU instances found (stub logic). Fill find_idle_gpus() to make this real.")
        return
    results = stop_instances(idle, dry_run=not args.apply)
    for r in results:
        print(f"{r.instance_id}: {r.action} – {r.reason}")

def cmd_optimize_prompt(args: argparse.Namespace) -> None:
    prompt = args.prompt
    async def run():
        variant = await optimize_prompt(prompt)
        print("=== ORIGINAL PROMPT ===\n")
        print(variant.original)
        print("\n=== OPTIMIZED PROMPT ===\n")
        print(variant.optimized)
        print("\nEstimated token savings:", variant.estimated_token_savings, "%")
        print("Notes:", variant.notes)
    asyncio.run(run())

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aifinops",
        description="AiFinOps – v0.1 MVP (v1–v5 steps wired into a single CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(
            """\
            Versions:
              v1 – ingest AWS daily costs
              v2 – explain bill with LLM
              v3 – suggest optimizations
              v4 – sweep idle GPU instances (dry-run)
              v5 – prompt optimizer for LLM apps
            """
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    s1 = sub.add_parser("ingest-aws", help="Fetch last N days of AWS costs (v1)")
    s1.add_argument("--days", type=int, default=3)
    s1.set_defaults(func=cmd_ingest)

    s2 = sub.add_parser("explain-bill", help="Explain AWS bill using LLM (v2/v3)")
    s2.add_argument("--days", type=int, default=3)
    s2.set_defaults(func=cmd_explain)

    s3 = sub.add_parser("sweep-gpus", help="Find + stop idle GPU instances (v4 – dry-run by default)")
    s3.add_argument("--threshold", type=int, default=30, help="Idle threshold in minutes")
    s3.add_argument("--apply", action="store_true", help="Actually stop instances (not just dry-run)")
    s3.set_defaults(func=cmd_sweep_gpus)

    s4 = sub.add_parser("optimize-prompt", help="LLM prompt optimizer (v5)")
    s4.add_argument("prompt", type=str, help="Prompt text to optimize")
    s4.set_defaults(func=cmd_optimize_prompt)

    return p

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
