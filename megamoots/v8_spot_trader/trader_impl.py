"""
Spot trader simulation:
- Accepts lists of market offers, performs simple auctions
- Provides fallback plan when preempted
"""
def choose_market(offers):
    # offers: list of {"cloud":..,"price":..,"reliability":..}
    # choose min price with penalty for low reliability
    def score(o):
        return o["price"] * (1 + (1 - o.get("reliability",1))*0.5)
    return min(offers, key=score)
