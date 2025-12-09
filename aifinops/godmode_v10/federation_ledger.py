class FederationLedger:
    def __init__(self):
        self.blocks = []
    def record(self, tx):
        self.blocks.append(tx)
    def history(self):
        return self.blocks
