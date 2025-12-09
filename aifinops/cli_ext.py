from __future__ import annotations
import argparse
import asyncio
from .aws_cost_fetcher import fetch_aws_daily_costs
from .attribution import attribute_costs, suggest_tags_for_unallocated
from .rightsizing import rightsizing_suggestions
from .zombie import find_zombies
from .lifecycle_predictor import predict_idle_windows
from .multicloud import fetch_azure_costs, fetch_gcp_costs
from .llm_guard import monitor_llm_costs
from .terraform_ai import generate_terraform_changes
from .slackbot import post_message
from .k8s_analyzer import analyze_k8s_waste
from .hybrid_forecast import hybrid_forecast
from .profitability import compute_profitability

def cmd_attr(args):
    items = fetch_aws_daily_costs(days=args.days)
    print("Attribution:")
    print(attribute_costs(items))

def cmd_rightsize(args):
    items = fetch_aws_daily_costs(days=args.days)
    print("Rightsizing suggestions:")
    print(rightsizing_suggestions(items))

def cmd_zombies(args):
    items = fetch_aws_daily_costs(days=args.days)
    print("Zombies:")
    print(find_zombies(items))

def cmd_predict(args):
    items = fetch_aws_daily_costs(days=args.days)
    print("Predicted idle windows:")
    print(predict_idle_windows(items))

def cmd_multicloud(args):
    print("Azure sample:", fetch_azure_costs(days=args.days))
    print("GCP sample:", fetch_gcp_costs(days=args.days))

def cmd_llmguard(args):
    # sample metrics
    metrics = {"openai": 123.4, "xai": 23.2}
    print(monitor_llm_costs(metrics, limit_monthly=args.limit))

def cmd_terraform_ai(args):
    # sample suggestion payload
    suggestions = [{"change":"downsize","resource":"i-123","to":"m5.medium"}]
    print(generate_terraform_changes(suggestions))

def cmd_slack(args):
    print(post_message(args.channel, args.text))

def cmd_k8s(args):
    print(analyze_k8s_waste([]))

def cmd_profit(args):
    costs = {"compute": 1200}
    revs = {"product": 5000}
    print(compute_profitability(costs, revs))

def build_parser():
    p = argparse.ArgumentParser(prog='aifinops-ext')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('attr'); s.add_argument('--days', type=int, default=7); s.set_defaults(func=cmd_attr)
    s = sub.add_parser('rightsize'); s.add_argument('--days', type=int, default=30); s.set_defaults(func=cmd_rightsize)
    s = sub.add_parser('zombies'); s.add_argument('--days', type=int, default=30); s.set_defaults(func=cmd_zombies)
    s = sub.add_parser('predict'); s.add_argument('--days', type=int, default=7); s.set_defaults(func=cmd_predict)
    s = sub.add_parser('multicloud'); s.add_argument('--days', type=int, default=7); s.set_defaults(func=cmd_multicloud)
    s = sub.add_parser('llmguard'); s.add_argument('--limit', type=float, default=1000.0); s.set_defaults(func=cmd_llmguard)
    s = sub.add_parser('terraform_ai'); s.set_defaults(func=cmd_terraform_ai)
    s = sub.add_parser('slack'); s.add_argument('--channel', default='#general'); s.add_argument('--text', default='hello'); s.set_defaults(func=cmd_slack)
    s = sub.add_parser('k8s'); s.set_defaults(func=cmd_k8s)
    s = sub.add_parser('profit'); s.set_defaults(func=cmd_profit)
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
