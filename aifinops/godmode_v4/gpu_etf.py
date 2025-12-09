class GPUETF:
    def __init__(self, weights):
        self.weights = weights

    def price(self, prices):
        total = 0
        for gpu, w in self.weights.items():
            for prov, p in prices.items():
                if gpu in p:
                    total += p[gpu] * w
                    break
        return round(total, 3)
