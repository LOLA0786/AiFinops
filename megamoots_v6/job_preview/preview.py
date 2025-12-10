def preview_job(model_name, hours, gpu_type="A100"):
    gpu_cost_map = {"A100": 4.2, "H100": 6.8, "A10G": 1.9}
    rate = gpu_cost_map.get(gpu_type, 4.0)
    total = round(rate * hours * 8, 2) # assume 8 GPUs
    return {
        "model": model_name,
        "gpu_type": gpu_type,
        "expected_duration_hours": hours,
        "cost_estimate": total,
        "recommendation": "Use spot + checkpointing to reduce 40-60% cost"
    }
