def recommend_gpu(model_size_gb, batch_size, training_hours):
    # Simple heuristic for demo
    if model_size_gb > 80:
        return "H100 80GB", "Best for extremely large models"
    if model_size_gb > 40:
        return "A100 80GB", "Balanced memory + throughput"
    if batch_size < 32:
        return "A10G", "Cost efficient for smaller models"
    return "A100 40GB", "General-purpose high-performance choice"
