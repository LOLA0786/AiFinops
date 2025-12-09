import asyncio
import streamlit as st
import pandas as pd
import numpy as np
import os

from aifinops.aws_cost_fetcher import fetch_aws_daily_costs
from aifinops.agent import explain_bill
from aifinops.anomaly import detect_anomalies
from aifinops.simulator import simulate_downsize, simulate_spot_replacement, simulate_reserved_savings
from aifinops.utilization import find_low_cpu_instances
from aifinops.gpu_heatmap import build_gpu_heatmap
from aifinops.spot_planner import estimate_spot_savings, recommend_spot_mix
from aifinops.forecasting_prophet import prophet_forecast
from aifinops.actions_ui import ui_stop_idle_instances
from aifinops.tagging_ai import suggest_tags_for_resources, generate_terraform_tag_snippets
from aifinops.tagging_apply import apply_tags_ec2
from aifinops.llm_clients import LLMClient

st.set_page_config(page_title="AiFinOps Dashboard (Pro+)", layout="wide")
st.title("AiFinOps Dashboard — Pro+")

# Controls
days = st.sidebar.slider("Days", 1, 90, 14)
region = st.sidebar.text_input("AWS Region", "us-east-1")
confirm_flag = os.getenv("CONFIRM_AUTO_ACTIONS", "false").lower() in ("1","true","yes")
llm_provider = os.getenv("LLM_PROVIDER", "openai")

# Fetch cost data
items = fetch_aws_daily_costs(days=days)
df = pd.DataFrame([{"date": i.date, "service": i.service, "amount": i.amount} for i in items])

st.header("Raw cost data")
if df.empty:
    st.warning("No cost data available.")
else:
    st.dataframe(df)

# Prophet Forecasting
st.header("Forecast (Prophet)")
if st.button("Run Prophet forecast"):
    with st.spinner("Fitting Prophet (may take a few seconds)..."):
        fc = prophet_forecast(items, days_ahead=14)
        fdf = pd.DataFrame(fc, columns=["date", "predicted"])
        fdf["date"] = pd.to_datetime(fdf["date"])
        fdf = fdf.set_index("date")
        st.line_chart(fdf)
        st.table(fdf.tail(10))

# Streaming AI Explanation (OpenAI streaming)
st.header("Streaming AI Explanation")
prompt_box = st.empty()
if st.button("Explain (streaming)"):
    # build prompt
    table_lines = [f"{c.date}\t{c.service}\t{c.amount:.4f}" for c in items]
    system_prompt = "You are a strict FinOps assistant. Provide Explanation and Optimization Suggestions."
    user_prompt = "COST TABLE:\n" + "\n".join(table_lines) + "\n\nReturn two sections: ### Explanation ### Optimization Suggestions"

    client = LLMClient(provider=llm_provider)
    placeholder = st.empty()
    # stream chunks
    try:
        for chunk in client.stream_openai_chat(user_prompt, system=system_prompt):
            existing = prompt_box.text_area("AI stream", value=(prompt_box.get_value() or "") + chunk, height=240)
            # small timeout to allow UI to refresh
    except Exception as e:
        st.error("Streaming failed: " + str(e))

# Tagging apply UI
st.header("Auto-tagging & Apply (Safe/Gated)")
resource_lines = st.text_area("Resources (one per line: instance-id,type,name)", height=120)
tag_key = st.text_input("Tag key to apply", "team")
tag_val = st.text_input("Tag value to apply", "infra")
if st.button("Suggest tags (LLM)"):
    resources = []
    for line in resource_lines.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            resources.append({"id": parts[0], "type": parts[1], "name": parts[2]})
    suggestion = suggest_tags_for_resources(resources)
    st.code(suggestion)
    st.code(generate_terraform_tag_snippets(resources))

if st.button("APPLY TAGS to EC2 (gated)"):
    resources = []
    for line in resource_lines.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            resources.append({"id": parts[0], "type": parts[1], "name": parts[2]})
    ec2_ids = [r["id"] for r in resources if r["type"].lower() == "ec2"]
    if not ec2_ids:
        st.info("No EC2 instance IDs found.")
    else:
        # call apply_tags_ec2 (dry_run False only if CONFIRM_AUTO_ACTIONS=true)
        dry_run = not confirm_flag
        try:
            res = apply_tags_ec2(ec2_ids, {tag_key: tag_val}, region=region, dry_run=dry_run)
            st.json(res)
        except PermissionError as e:
            st.error(str(e))

# GPU heatmap
st.header("GPU Idle Heatmap (Pro)")
iids = st.text_input("GPU Instance IDs (comma separated)", "")
if st.button("Build GPU heatmap"):
    ids = [x.strip() for x in iids.split(",") if x.strip()]
    heat = build_gpu_heatmap(ids, minutes=60, region=region)
    st.table(pd.DataFrame([{"instance_id": k, "gpu_util": v} for k, v in heat.items()]))

# EC2 spot planner
st.header("EC2 → Spot Conversion Planner")
if st.button("Estimate spot conversion"):
    s, note = estimate_spot_savings(items)
    st.info(note)
    for r in recommend_spot_mix(items):
        st.write("- " + r)

st.success("Pro features loaded. Use CONFIRM_AUTO_ACTIONS=true to enable real apply operations (dangerous).")

# ---- GPU Optimizer Panel ----
try:
    from aifinops.gpu_dashboard import render_gpu_overview, render_gpu_issues_and_explain, render_cost_estimator
    st.header("GPU Optimizer")
    render_gpu_overview()
    render_gpu_issues_and_explain()
    render_cost_estimator()
except Exception as e:
    st.warning("GPU panel load failed: " + str(e))

st.header("GPU Insights (K8s & Training)")
try:
    from aifinops.k8s_gpu import list_gpu_pods, map_nodes_with_gpus
    from aifinops.training_log_parser import parse_training_log, build_llm_prompt
    from aifinops.gpu_heatmap_weekly import aggregate_gpu_timeseries, write_pr_snippet
    st.subheader("Kubernetes GPU Pods")
    pods = list_gpu_pods() or []
    if pods:
        st.write("GPU pods sample:", pods[:10])
    else:
        st.info("No GPU pods found or no K8s access.")

    st.subheader("Training Log Analysis (paste sample logs)")
    txt = st.text_area("Paste training log tail (200 lines)", height=200)
    if st.button("Analyze logs"):
        summary = parse_training_log(txt)
        st.json(summary)
        prompt = build_llm_prompt("You are diagnosing training problems.", summary)
        st.code(prompt)

    st.subheader("Weekly Heatmap + PR generator")
    st.info("Upload timeseries JSON of {ts,gpu_index,gpu_util} or use local monitor output.")
    uploaded = st.file_uploader("Timeseries JSON", type=["json"])
    if uploaded:
        import json
        samples = json.load(uploaded)
        pivot = aggregate_gpu_timeseries(samples)
        st.dataframe(pivot)
        if st.button("Generate PR snippet"):
            # naive recommendations: if avg util < 10 -> scale down
            recs = []
            avg = pivot.mean().to_dict()
            for k,v in avg.items():
                if v < 10:
                    recs.append({"node":str(k),"instance":"p4d.24xlarge","issue":"low_util","suggest":"scale-to-0-or-spot"})
            path = write_pr_snippet(recs)
            st.success(f"Wrote PR snippet to {path}")
except Exception as e:
    st.warning("GPU Insights load failed: " + str(e))
