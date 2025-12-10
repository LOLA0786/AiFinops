"""
Simple GPU price oracle scaffold.
Implement real scrapers / cloud SDK integrations in prod.
"""
def sample_prices():
    return {
        "aws": {"A100": 3.2, "H100": 6.5},
        "gcp": {"A100": 2.9, "TPU-v5e": 4.0},
        "azure": {"H100": 6.8, "MI300X": 7.0}
    }

def find_best(gpu_type="A100"):
    prices = sample_prices()
    best = None
    for cloud, pmap in prices.items():
        if gpu_type in pmap:
            price = pmap[gpu_type]
            if best is None or price < best[1]:
                best = (cloud, price)
    return best

if __name__=="__main__":
    print(find_best("A100"))
