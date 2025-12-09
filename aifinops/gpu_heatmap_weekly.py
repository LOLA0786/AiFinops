from __future__ import annotations
import pandas as pd
import datetime as dt
import os
from typing import List, Dict, Tuple

def aggregate_gpu_timeseries(samples: List[Dict], window_days: int = 7) -> pd.DataFrame:
    """
    samples: list of {"ts": ISO, "gpu_index": int, "gpu_util": float}
    returns pivot table index=hour, cols=gpu_index
    """
    if not samples:
        return pd.DataFrame()
    df = pd.DataFrame(samples)
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.set_index('ts').sort_index()
    df = df.resample('1H').mean().fillna(0)
    df['hour'] = df.index
    pivot = df.pivot_table(index=df.index, columns='gpu_index', values='gpu_util', aggfunc='mean').fillna(0)
    return pivot

def write_pr_snippet(recommendations: List[Dict], out_path: str = "finops/actions/gpu_pr_snippet.txt") -> str:
    """
    Writes a human-friendly PR snippet describing actions (helm/terraform).
    recommendations: [{"node":"ip-...", "instance":"p4d.24xlarge","issue":"idle","suggest":"scale-to-0"}]
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("# Auto-generated GPU optimization suggestions\\n\\n")
        for r in recommendations:
            f.write(f"- Node: {r.get('node')} | Instance: {r.get('instance')} | Issue: {r.get('issue')}\\n")
            f.write(f"  Suggested action: {r.get('suggest')}\\n\\n")
        f.write("Please review before applying.\\n")
    return out_path
