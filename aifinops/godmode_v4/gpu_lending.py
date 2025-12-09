class GPULendingMarket:
    def __init__(self):
        self.supplied = {}
        self.borrowed = {}
        self.interest_rate = 0.12

    def supply(self, user, units):
        self.supplied[user] = self.supplied.get(user, 0) + units

    def borrow(self, user, units):
        self.borrowed[user] = self.borrowed.get(user, 0) + units

    def calculate_interest(self, user, days):
        return self.borrowed.get(user, 0) * (self.interest_rate / 365) * days
