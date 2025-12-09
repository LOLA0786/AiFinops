def recommend_gpu_placement(gpu_data):
    """
    gpu_data = {
      "aws": [{"gpu":"A100","util":0.2}],
      "gcp": [{"gpu":"L4","util":0.7}],
      "azure": [{"gpu":"MI300X","util":0.1}]
    }
    """
    recs = []
    for provider, items in gpu_data.items():
        for g in items:
            if g["util"] < 0.15:
                recs.append({
                    "provider": provider,
                    "gpu": g["gpu"],
                    "action": "scale-down / consolidate workloads"
                })
            elif g["util"] > 0.80:
                recs.append({
                    "provider": provider,
                    "gpu": g["gpu"],
                    "action": "scale-up or distribute load"
                })
    return recs
