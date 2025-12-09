from aifinops.godmode_v3.gpu_index import compute_global_gpu_index

class GPUEconomyGovernor:
    def __init__(self):
        self.rate = 0.05

    def adjust_policy(self, spot_prices):
        ggx = compute_global_gpu_index(spot_prices)
        if ggx > 4.0:
            self.rate += 0.01
        elif ggx < 2.0:
            self.rate -= 0.01
        return self.rate
