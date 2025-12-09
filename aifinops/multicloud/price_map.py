GPU_PRICES = {
    "aws": {"A100": 2.39, "H100": 4.99},
    "gcp": {"A100": 2.20, "L4": 0.68, "H100": 4.70},
    "azure": {"A100": 2.35, "MI300X": 3.99}
}

def best_gpu_price(gpu_type):
    results = []
    for provider, data in GPU_PRICES.items():
        if gpu_type in data:
            results.append({
                "provider": provider,
                "price": data[gpu_type]
            })
    return sorted(results, key=lambda x: x["price"])
