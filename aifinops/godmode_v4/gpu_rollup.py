class GPURollup:
    def __init__(self):
        self.batch = []

    def add_tx(self, tx):
        self.batch.append(tx)

    def produce_rollup(self):
        root_hash = hash(str(self.batch))
        block = {"root": root_hash, "txs": self.batch}
        self.batch = []
        return block
