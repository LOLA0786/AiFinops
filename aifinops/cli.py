from __future__ import annotations

import argparse
import asyncio
from textwrap import dedent

from .aws_cost_fetcher import fetch_aws_daily_costs
from .agent import explain_bill, format_pr_body
from .anomaly import detect_anomalies
from .simulator import simulate_downsize, simulate_spot_replacement, simulate_reserved_savings
from .utilization import find_low_cpu_instances
from .github_pr import create_pr
from .prompt_optimizer import optimize_prompt

def cmd_ingest(args):
    items = fetch_aws_daily_costs(days=args.days)
    print(f"Fetched {len(items)} cost rows for last {args.days} days.\n")
    for c in items:
        print(f"{c.date} | {c.service:<40} | ${c.amount:.4f} {c.unit}")

def cmd_explain(args):
    items = fetch_aws_daily_costs(days=args.days)
    async def run():
        res = await explain_bill(items)
        print("=== EXPLANATION ===")
        print(res.summary)
        print("\n=== OPTIMIZATIONS ===")
        print(res.optimizations)
        print(f"\n(Provider used: {res.provider_used})")
    asyncio.run(run())

def cmd_detect(args):
    items = fetch_aws_daily_costs(days=args.days)
    anomalies = detect_anomalies(items)
    if not anomalies:
        print("No anomalies detected.")
        return
    for svc, lst in anomalies.items():
        print(f"Service: {svc}")
        for it in lst:
            print(f" - {it.date}: ${it.amount:.2f}")

def cmd_simulate(args):
    items = fetch_aws_daily_costs(days=args.days)
    if args.action == "downsize":
        s, note = simulate_downsize(items, svc_name=args.service, down_pct=args.pct)
    elif args.action == "spot":
        s, note = simulate_spot_replacement(items, svc_name=args.service, spot_pct=args.pct)
    else:
        s, note = simulate_reserved_savings(items, svc_name=args.service, reserve_pct=args.pct)
    print(note)
    print(f"Projected monthly savings: ${s:.2f}")

def cmd_util(args):
    print("Scanning for low-CPU instances (may require AWS credentials)...")
    low = find_low_cpu_instances(region=args.region, minutes=args.minutes, threshold=args.threshold)
    if not low:
        print("No low-CPU instances found or AWS not configured.")
        return
    for i in low:
        print(f"{i['InstanceId']} ({i['InstanceType']}): avg CPU {i['AvgCPU']:.2f}%")

def cmd_pr(args):
    items = fetch_aws_daily_costs(days=args.days)
    async def run():
        exp = await explain_bill(items)
        body = format_pr_body(items, exp)
        if args.push:
            url = create_pr(args.repo, args.branch, args.title, body, push=True)
            if url:
                print("PR URL:", url)
        else:
            print("=== PR BODY (dry-run) ===")
            print(body)
    asyncio.run(run())

def cmd_optimize_prompt(args):
    prompt = args.prompt
    async def run():
        var = await optimize_prompt(prompt)
        print("Original:", var.original)
        print("\nOptimized:", var.optimized)
        print("\nEst savings:", var.estimated_token_savings)
    asyncio.run(run())

def build_parser():
    p = argparse.ArgumentParser(prog="aifinops", formatter_class=argparse.RawDescriptionHelpFormatter,
                                description="AiFinOps CLI (extended)")
    sub = p.add_subparsers(dest="command", required=True)

    s1 = sub.add_parser("ingest-aws"); s1.add_argument("--days", type=int, default=3); s1.set_defaults(func=cmd_ingest)
    s2 = sub.add_parser("explain-bill"); s2.add_argument("--days", type=int, default=3); s2.set_defaults(func=cmd_explain)
    s3 = sub.add_parser("detect-anomalies"); s3.add_argument("--days", type=int, default=7); s3.set_defaults(func=cmd_detect)

    s4 = sub.add_parser("simulate"); 
    s4.add_argument("action", choices=["downsize","spot","reserve"])
    s4.add_argument("--service", type=str, default="AmazonEC2")
    s4.add_argument("--pct", type=float, default=0.5)
    s4.add_argument("--days", type=int, default=30)
    s4.set_defaults(func=cmd_simulate)

    s5 = sub.add_parser("analyze-util"); 
    s5.add_argument("--minutes", type=int, default=60)
    s5.add_argument("--threshold", type=float, default=5.0)
    s5.add_argument("--region", type=str, default="us-east-1")
    s5.set_defaults(func=cmd_util)

    s6 = sub.add_parser("create-pr");
    s6.add_argument("--repo", required=True, help="owner/repo")
    s6.add_argument("--branch", default="aifinops-cost-fix")
    s6.add_argument("--title", default="AiFinOps cost optimization suggestions")
    s6.add_argument("--days", type=int, default=3)
    s6.add_argument("--push", action="store_true", help="Actually create PR (requires GITHUB_TOKEN)")
    s6.set_defaults(func=cmd_pr)

    s7 = sub.add_parser("optimize-prompt"); s7.add_argument("prompt", type=str); s7.set_defaults(func=cmd_optimize_prompt)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
