# MegaMoats Implementation Pack v2 - Local Quickstart

This pack contains production-like implementations for moats v1..v10 and a synthetic simulator.

Quick steps:

1. Generate synthetic data and run a simple demo:
   ./run_local_demo.sh

2. Run unit tests:
   pip install pytest
   pytest -q

3. Inspect simulator output:
   sim/output/telemetry.jsonl
   sim/output/training_logs.txt
   sim/output/market_signals.jsonl

Notes:
- The telemetry implementation uses NVML if pynvml is installed; otherwise it uses a deterministic simulator.
- The FinOps optimizer is rule-based; you can integrate an LLM endpoint by editing v10_finops_llm_optimizer/optimizer_impl.py
