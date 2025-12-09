class GPUWorldBank:
    def __init__(self):
        self.loans = {}

    def issue_loan(self, borrower, compute_units, interest):
        self.loans[borrower] = {"units": compute_units, "interest": interest}
        return self.loans[borrower]
