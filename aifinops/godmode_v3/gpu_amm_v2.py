class GPU_AMM_V2:
    def __init__(self):
        self.liquidity = {}
    def add_liquidity(self, gpu, provider, units):
        pool = self.liquidity.setdefault(gpu, {})
        pool[provider] = pool.get(provider, 0) + units
    def quote(self, gpu, provider):
        return 1 / self.liquidity.get(gpu, {}).get(provider, 1)
    def swap(self, gpu, from_provider, to_provider, amount):
        r = self.liquidity[gpu]
        x, y = r[from_provider], r[to_provider]
        k = x * y
        x_new = x + amount
        y_new = k / x_new
        out = y - y_new
        r[from_provider] = x_new; r[to_provider] = y_new
        return out
