"""
FinOps optimizer:
- Rule-based optimizer that suggests actions
- LLM stub to format recommendations if user has an LLM server
"""
def suggest_changes(bill, metrics):
    recs = []
    monthly = bill.get("monthly",0)
    if monthly > 10000:
        recs.append("consider_spot_instances")
        recs.append("reduce_overprovisioning")
    if metrics.get("avg_gpu_util",0) < 20:
        recs.append("consolidate_jobs")
    return recs

def format_with_llm(recs, llm_endpoint=None):
    # llm_endpoint optional: if provided, we would call it.
    # For offline use we return a well-formed text
    return "Recommendations:\\n" + "\\n".join(f"- {r}" for r in recs)
