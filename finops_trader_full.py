#!/usr/bin/env python3
"""
FinOps Trading Logic — MegaMoats v5 demo scaffold
Place as: demo_v5/finops_trader_full.py

Purpose:
 - Demonstrates checkpointing guidance, bidding strategy, hybrid 
allocation,
   real-time optimization (idle/zombie/right-size), and a simple cost 
forecast.
 - Uses pure Python stdlib only (no external dependencies).
 - Fake data generator included for demo/testing.

Run:
  PYTHONPATH=. python demo_v5/finops_trader_full.py
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time
import random
import statistics
import math
import argparse

# -------------------------
# Helper & Data Structures
# -------------------------
@dataclass
class JobInfo:
    job_id: str
    gpu_type: str  # e.g., "A100", "H100", "V100"
    gpu_count: int
    priority: int  # 0 = low, 10 = critical
    runtime_min: float  # expected runtime in minutes
    last_active_ts: float  # epoch seconds last GPU activity
    team: str = "unknown"
    checkpoint_supported: bool = True

@dataclass
class PriceSample:
    ts: float
    provider: str  # 'aws', 'gcp', 'lambda', etc
    zone: str
    instance: str
    price_per_hour: float

# -------------------------
# Checkpointing Advisor
# -------------------------
class Checkpointer:
    """Simple checkpoint advisor."""

    INTERRUPT_THRESHOLD_SECONDS = 60  # emulate time to interruption 
notice

    def __init__(self):
        pass

    def should_checkpoint(self, job: JobInfo, spot_risk_score: float) -> 
bool:
        """
        Decide to checkpoint if job is spot, long-running, or high 
interruption risk.
        spot_risk_score: 0..1 where 1 is high risk of interruption.
        """
        if not job.checkpoint_supported:
            return False
        long_running = job.runtime_min > 30  # >30 min worth 
checkpointing more aggressively
        if job.priority >= 8:
            # critical jobs: prefer reserved/on-demand - but if on spot 
and risk high, checkpoint
            return spot_risk_score > 0.15
        # Checkpoint when risk or long running
        return long_running and spot_risk_score > 0.05

    def auto_checkpoint_before_interruption(self, job: JobInfo):
        # Placeholder: in prod this would invoke model save hooks
        print(f"[checkpoint] Auto-checkpointing job {job.job_id} 
(gpu_type={job.gpu_type})")

# -------------------------
# Bidding Strategy
# -------------------------
class BiddingStrategy:
    """Historic price analysis + zone switching + fallback logic."""

    def __init__(self, price_history: List[PriceSample]):
        self.price_history = price_history  # list of PriceSample

    def average_price(self, provider: str, instance: str, zone: 
Optional[str] = None) -> float:
        samples = [p.price_per_hour for p in self.price_history
                   if p.provider == provider and p.instance == instance 
and (zone is None or p.zone == zone)]
        if not samples:
            return float("inf")
        return statistics.mean(samples)

    def recommend_bid(self, desired_instance: str, providers: List[str]) 
-> Tuple[str, str, float]:
        """
        Recommend (provider, zone, bid_price)
        Strategy:
         - For each provider/zone sample for desired instance compute 
median price
         - Choose lowest median and recommend bid = median * (1 + 
safety_margin)
         - Safety margin depends on volatility (stddev / mean)
        """
        candidates = []
        inst = desired_instance
        for p in self.price_history:
            if p.instance != inst:
                continue
            candidates.append((p.provider, p.zone, p.price_per_hour))
        if not candidates:
            return (providers[0], "any", 999.0)
        # aggregate by provider+zone
        by_zone: Dict[Tuple[str,str], List[float]] = {}
        for provider, zone, price in candidates:
            by_zone.setdefault((provider, zone), []).append(price)
        best = None
        for (provider, zone), prices in by_zone.items():
            meanp = statistics.mean(prices)
            stdp = statistics.pstdev(prices) if len(prices) > 1 else 0.0
            volatility = (stdp / meanp) if meanp > 0 else 0.0
            safety = 0.08 + min(0.2, volatility * 0.5)  # 8% baseline + 
small extra for volatility
            bid = meanp * (1 + safety)
            if best is None or bid < best[2]:
                best = (provider, zone, bid)
        # fallback to other instance classes if nothing found would be 
implemented elsewhere
        return best

    def instance_fallbacks(self, gpu_type: str) -> List[str]:
        """Return a prioritized list of acceptable fallback instance 
types for a gpu_type."""
        mapping = {
            "H100": ["H100", "A100", "A40"],
            "A100": ["A100", "V100", "T4"],
            "V100": ["V100", "T4"]
        }
        return mapping.get(gpu_type, [gpu_type])

# -------------------------
# Hybrid Allocation Rules
# -------------------------
class HybridAllocator:
    """Decide allocation class (reserved/on-demand/spot) based on job 
requirements"""

    def decide_allocation(self, job: JobInfo) -> str:
        if job.priority >= 9:
            return "reserved"
        if job.runtime_min < 10 and job.priority < 5:
            return "spot"
        if job.runtime_min > 120 and job.priority < 6:
            # long training, use spot with checkpointing
            return "spot-with-checkpoint"
        return "on-demand"

# -------------------------
# Real-Time Optimizer
# -------------------------
class RealTimeOptimizer:
    """Real-time checks: idle GPUs, zombies, right-sizing, 
recommendations."""

    def __init__(self):
        pass

    def detect_idle(self, job: JobInfo, now_ts: float, 
idle_threshold_minutes: float = 5.0) -> bool:
        idle_secs = now_ts - job.last_active_ts
        return idle_secs > idle_threshold_minutes * 60 and (job.priority 
< 8)

    def detect_zombie(self, pod_state: Dict) -> bool:
        """pod_state is a dict with fields like {'active': False, 
'gpu_attached': True}"""
        return not pod_state.get('active', True) and 
pod_state.get('gpu_attached', False)

    def right_size(self, job: JobInfo, observed_gpu_mem_used_gb: float) 
-> Optional[str]:
        """
        Suggest right-size: if using 80GB A100 but job uses < 16GB, 
recommend smaller instance or fractional plan.
        Returns recommendation string or None.
        """
        big_types = {"A100": 80, "H100": 80, "V100": 32}
        cap = big_types.get(job.gpu_type, None)
        if cap and observed_gpu_mem_used_gb < min(0.25 * cap, 16):
            return f"Right-size: consider moving {job.job_id} to smaller 
GPU or MIG fractional allocation"
        return None

    def recommend_cheaper_alternative(self, job: JobInfo, 
perf_requirement: Dict) -> Optional[str]:
        """
        perf_requirement example: {'min_tflops': 100}
        Very naive: if job doesn't need top performance, suggest cheaper 
GPU family.
        """
        if job.gpu_type == "H100" and perf_requirement.get('min_tflops', 
0) < 200:
            return "Consider A100 instead of H100 for this workload"
        return None

# -------------------------
# Predictive Cost Forecaster
# -------------------------
class CostForecaster:
    """Lightweight forecasting using exponential smoothing on historic 
spend/time-series."""

    def __init__(self, series: List[float]):
        self.series = list(series)

    def simple_exponential_smoothing(self, alpha: float = 0.3, steps: 
int = 24) -> List[float]:
        """Return forecast for next `steps` timepoints (hours)."""
        if not self.series:
            return [0.0] * steps
        s = self.series[0]
        for x in self.series[1:]:
            s = alpha * x + (1 - alpha) * s
        forecasts = []
        last = s
        # naive: forecast repeats the smoothed level (could be extended)
        for _ in range(steps):
            # add small noise for variability demonstration only
            forecasts.append(round(last * (1 + random.uniform(-0.02, 
0.02)), 4))
        return forecasts

    def alert_if_overspend(self, current_monthly_runrate: float, 
budget_limit: float) -> Optional[str]:
        if current_monthly_runrate > budget_limit:
            over = current_monthly_runrate - budget_limit
            pct = (over / budget_limit) * 100
            return f"ALERT: Projected overspend ${over:,.0f} 
({pct:.1f}%) this month"
        return None

# -------------------------
# Fake Data Generator (for demo)
# -------------------------
def make_fake_price_history() -> List[PriceSample]:
    now = time.time()
    samples = []
    providers = ["aws", "gcp", "lambda"]
    zones = ["us-east-1a", "us-east-1b", "us-west-2a"]
    instances = ["A100", "H100", "V100"]
    for i in range(120):
        ts = now - (120 - i) * 3600  # hourly samples 120 hours back
        for prov in providers:
            for zone in zones:
                for inst in instances:
                    base = {"A100": 3.2, "H100": 6.5, "V100": 
1.8}.get(inst, 3.0)
                    # simulate price noise
                    price = round(base * (1 + random.uniform(-0.18, 
0.18)), 3)
                    samples.append(PriceSample(ts=ts, provider=prov, 
zone=zone, instance=inst, price_per_hour=price))
    return samples

def make_fake_jobs() -> List[JobInfo]:
    now = time.time()
    return [
        JobInfo(job_id="job-1001", gpu_type="A100", gpu_count=4, 
priority=5, runtime_min=180, last_active_ts=now-30, team="vision"),
        JobInfo(job_id="job-1002", gpu_type="H100", gpu_count=8, 
priority=9, runtime_min=600, last_active_ts=now-10, team="llm", 
checkpoint_supported=True),
        JobInfo(job_id="job-1003", gpu_type="A100", gpu_count=1, 
priority=2, runtime_min=15, last_active_ts=now-600, team="prod", 
checkpoint_supported=False),
    ]

# -------------------------
# Demo Runner (glues everything)
# -------------------------
def run_demo():
    print("\n=== MegaMoats v5 — FinOps Trader Demo (scaffold) ===\n")
    price_history = make_fake_price_history()
    jobs = make_fake_jobs()

    # Instantiate modules
    checker = Checkpointer()
    bidder = BiddingStrategy(price_history)
    allocator = HybridAllocator()
    rtopt = RealTimeOptimizer()
    # build a fake spend time-series (hourly last 72 hours)
    spend_series = [round(2000 + 200 * math.sin(i/6.0) + 
random.uniform(-100, 100), 2) for i in range(72)]
    forecaster = CostForecaster(spend_series)

    # 1) Bidding recommendations
    print("[1] Bidding recommendations (desired=A100)")
    prov, zone, bid = bidder.recommend_bid("A100", 
providers=["aws","gcp","lambda"])
    print(f"  Recommended provider={prov} zone={zone} 
bid_price=${bid:.3f}/hr\n")

    # 2) Allocation decisions
    print("[2] Allocation decisions")
    for j in jobs:
        alloc = allocator.decide_allocation(j)
        print(f"  Job {j.job_id}: allocation -> {alloc}")
    print("")

    # 3) Checkpointing logic
    print("[3] Checkpointing advisor")
    # fake spot risk for each job (0..1)
    for j in jobs:
        risk = random.uniform(0.0, 0.4)
        should_cp = checker.should_checkpoint(j, risk)
        print(f"  Job {j.job_id} (priority={j.priority}, 
runtime_min={j.runtime_min}) spot_risk={risk:.2f} -> 
checkpoint={should_cp}")
        if should_cp and j.checkpoint_supported:
            checker.auto_checkpoint_before_interruption(j)
    print("")

    # 4) Real-time optimizations: idle detection / zombies / right-size
    print("[4] Real-time optimization checks")
    now = time.time()
    for j in jobs:
        idle = rtopt.detect_idle(j, now, idle_threshold_minutes=5.0)
        rightsize = rtopt.right_size(j, 
observed_gpu_mem_used_gb=random.uniform(4, 60))
        print(f"  Job {j.job_id}: idle={idle} 
rightsize_recommendation={rightsize}")
    # fake pod state example
    pod_state = {'active': False, 'gpu_attached': True}
    print(f"  Example pod state {pod_state} -> 
zombie={rtopt.detect_zombie(pod_state)}\n")

    # 5) Predictive cost forecast
    print("[5] Predictive cost forecast (next 24h)")
    forecast = forecaster.simple_exponential_smoothing(alpha=0.25, 
steps=24)
    print(f"  Next 24h forecast (sampled): {forecast[:6]} ...")
    # alert if monthly runrate > budget (simple calculation)
    current_runrate = sum(forecast) * 30  # rough monthly
    alert = forecaster.alert_if_overspend(current_runrate, 
budget_limit=100000.0)
    print(f"  Monthly runrate estimate: ${current_runrate:,.0f}")
    if alert:
        print("  " + alert)
    else:
        print("  Budgeting: OK\n")

    # 6) Full action summary
    print("[6] Action summary (example)")
    print("  - Launch bid on provider:", prov, "zone:", zone, f"@ 
${bid:.3f}/hr")
    print("  - Auto-checkpoint will run for flagged long-running spot 
jobs.")
    print("  - Idle GPUs will be reclaimed after grace period.")
    print("  - Scheduler will prefer cheaper provider where perf 
acceptable.\n")

    print("=== Demo complete ===\n")

# -------------------------
# CLI Entrypoint
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="finops_trader_full.py", 
description="Run MegaMoats FinOps Trader demo")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    args = parser.parse_args()
    if args.demo or True:
        run_demo()

