def compute_global_gpu_index(prices):
    total = 0; count = 0
    for prov in prices.values():
        for px in prov.values():
            total += px; count += 1
    return round(total / max(1, count), 4)
