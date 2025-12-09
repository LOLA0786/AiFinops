class GPUYieldFarm:
    def __init__(self):
        self.total_liquidity = 0
        self.lp_shares = {}
        self.rewards = {}

    def stake(self, user, units):
        self.total_liquidity += units
        self.lp_shares[user] = self.lp_shares.get(user, 0) + units

    def distribute_rewards(self, reward):
        for user, stake in self.lp_shares.items():
            portion = stake / self.total_liquidity
            self.rewards[user] = self.rewards.get(user, 0) + reward * portion
