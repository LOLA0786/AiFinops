from price_oracle import aggregate

def find_best_price(gpu_type):
    markets = aggregate()
    best = None

    for cloud, prices in markets.items():
        if gpu_type in prices:
            price = prices[gpu_type]
            if best is None or price < best[1]:
                best = (cloud, price)

    return best
