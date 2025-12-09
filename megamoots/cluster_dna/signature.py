def signature_from_metrics(metrics):
    return {
        "nodes": metrics.get("nodes", 1),
        "avg_gpu_util": metrics.get("avg_gpu_util", 0),
        "mem_pressure": metrics.get("mem_pressure", 0)
    }
