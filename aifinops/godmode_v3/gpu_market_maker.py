import random
class GPUMarketMaker:
    def __init__(self, orderbook, spread=0.05):
        self.ob = orderbook
        self.spread = spread
    def make_markets(self, gpu, mid):
        bid = mid * (1 - self.spread)
        ask = mid * (1 + self.spread)
        amt = random.uniform(1, 10)
        self.ob.add_bid(gpu, bid, amt)
        self.ob.add_ask(gpu, ask, amt)
        return {"bid": bid, "ask": ask, "amount": amt}
