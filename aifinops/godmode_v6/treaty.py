class GPUTreaty:
    def __init__(self, parties, compute_terms):
        self.parties = parties
        self.compute_terms = compute_terms
        self.active = True

    def terminate(self):
        self.active = False
