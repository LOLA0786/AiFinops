# GPU ORDERBOOK ENGINE
class GPUOrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}
    def add_bid(self, gpu, price, amount):
        self.bids.setdefault(gpu, [])
        self.bids[gpu].append((price, amount))
        self.bids[gpu] = sorted(self.bids[gpu], key=lambda x: -x[0])
    def add_ask(self, gpu, price, amount):
        self.asks.setdefault(gpu, [])
        self.asks[gpu].append((price, amount))
        self.asks[gpu] = sorted(self.asks[gpu], key=lambda x: x[0])
    def match_orders(self, gpu):
        trades = []
        bids = self.bids.get(gpu, [])
        asks = self.asks.get(gpu, [])
        while bids and asks and bids[0][0] >= asks[0][0]:
            bid = bids.pop(0); ask = asks.pop(0)
            px = (bid[0] + ask[0]) / 2
            amt = min(bid[1], ask[1])
            trades.append({"gpu": gpu, "price": px, "amount": amt})
        self.bids[gpu] = bids; self.asks[gpu] = asks
        return trades
