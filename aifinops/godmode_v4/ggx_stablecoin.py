from aifinops.godmode_v3.gpu_index import compute_global_gpu_index

class GGXStablecoin:
    def __init__(self):
        self.balances = {}
        self.collateral_pool = 0

    def mint(self, user, amount, gpu_prices):
        peg = compute_global_gpu_index(gpu_prices)
        collateral_needed = amount * peg
        self.collateral_pool += collateral_needed
        self.balances[user] = self.balances.get(user, 0) + amount

    def burn(self, user, amount, gpu_prices):
        peg = compute_global_gpu_index(gpu_prices)
        collateral_release = amount * peg
        self.collateral_pool -= collateral_release
        self.balances[user] -= amount
        return collateral_release
