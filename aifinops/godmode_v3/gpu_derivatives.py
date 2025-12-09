class GPUDerivative:
    def __init__(self, gpu, notional, leverage=1):
        self.gpu = gpu
        self.notional = notional
        self.leverage = leverage
    def payoff(self, px_now, px_later):
        return (px_later - px_now) * self.notional * self.leverage
