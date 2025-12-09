from __future__ import annotations
import streamlit as st
import pandas as pd
import datetime as dt
from typing import List, Dict
from .gpu_optimizer_agent import collect_gpu_metrics_local, detect_gpu_issues, estimate_waste_cost

def render_gpu_overview():
    st.subheader("GPU Overview")
    samples = collect_gpu_metrics_local()
    if not samples:
        st.info("No local GPUs detected (nvidia-smi / NVML not available).")
        return
    df = pd.DataFrame(samples)
    df_display = df[["index","name","gpu_util","mem_util","mem_total","mem_used"]].rename(columns={"index":"GPU"})
    st.dataframe(df_display)

    st.write("Heatmap (current utilization)")
    st.bar_chart(df.set_index("index")[["gpu_util","mem_util"]])

def render_gpu_issues_and_explain(async_explain=False):
    st.subheader("GPU Issues")
    samples = collect_gpu_metrics_local()
    issues = detect_gpu_issues(samples)
    for it in issues:
        st.write(f"GPU {it['gpu_index']} — {it['name']}")
        st.write("Issues:", it["issues"])
    if st.button("Ask AI to explain & fix"):
        with st.spinner("Calling LLM (may be slower)…"):
            import asyncio
            from .gpu_optimizer_agent import explain_with_llm
            text = asyncio.run(explain_with_llm(issues, context="AiFinOps GPU analysis"))
            st.code(text)

def render_cost_estimator():
    st.subheader("GPU Waste Cost Estimator")
    hours = st.number_input("Estimated wasted GPU hours", min_value=0.0, value=10.0)
    price = st.number_input("GPU price per hour (USD)", min_value=0.0, value=36.0)
    est = estimate_waste_cost(hours, price)
    st.metric("Estimated waste (USD)", f"${est:,.2f}")
