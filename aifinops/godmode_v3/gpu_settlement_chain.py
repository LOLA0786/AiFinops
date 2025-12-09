class GPUSettlementChain:
    def __init__(self):
        self.ledger = []
        self.balances = {}
    def credit(self, user, amt):
        self.balances[user] = self.balances.get(user, 0) + amt
    def debit(self, user, amt):
        self.balances[user] -= amt
    def transfer(self, frm, to, amt):
        self.debit(frm, amt); self.credit(to, amt)
        self.ledger.append({"from": frm, "to": to, "amount": amt})
