class GPUTaxAuthority:
    def __init__(self):
        self.collected = 0

    def apply_tax(self, compute_cost, rate=5):
        tax = compute_cost * (rate / 100)
        self.collected += tax
        return compute_cost + tax
