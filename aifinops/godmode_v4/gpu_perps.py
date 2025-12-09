class GPUPerp:
    def __init__(self, gpu, entry_price, size, leverage):
        self.gpu = gpu
        self.entry = entry_price
        self.size = size
        self.leverage = leverage

    def pnl(self, current_price):
        return (current_price - self.entry) * self.size * self.leverage
