from matcher import find_best_price

def recommend(gpu):
    cloud, price = find_best_price(gpu)
    return f"Best price for {gpu}: {cloud} at ${price}/hour"
