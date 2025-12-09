from __future__ import annotations
from typing import List, Tuple
from .aws_cost_fetcher import CostItem

def simulate_downsize(items: List[CostItem], svc_name: str = "AmazonEC2", down_pct: float = 0.5) -> Tuple[float, str]:
    """
    Simulate reducing costs for a service by down_pct (e.g., 0.5 = 50% cheaper).
    Returns (monthly_savings, summary).
    """
    total = sum(i.amount for i in items if svc_name in i.service)
    savings = total * down_pct
    summary = f"Downsize {svc_name} by {down_pct*100:.0f}% -> estimated monthly savings ${savings:.2f}"
    return savings, summary

def simulate_spot_replacement(items: List[CostItem], svc_name: str = "AmazonEC2", spot_pct: float = 0.7) -> Tuple[float, str]:
    total = sum(i.amount for i in items if svc_name in i.service)
    savings = total * spot_pct
    summary = f"Replace flexible workloads with Spot -> estimated monthly savings ${savings:.2f}"
    return savings, summary

def simulate_reserved_savings(items: List[CostItem], svc_name: str = "AmazonEC2", reserve_pct: float = 0.3) -> Tuple[float, str]:
    total = sum(i.amount for i in items if svc_name in i.service)
    savings = total * reserve_pct
    summary = f"Buy savings plan/reserved instances -> estimated monthly savings ${savings:.2f}"
    return savings, summary
