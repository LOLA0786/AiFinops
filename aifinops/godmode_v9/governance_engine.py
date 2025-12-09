class GPUGovernanceEngine:
    def __init__(self):
        self.policies = {}

    def enact_policy(self, region, policy):
        self.policies[region] = policy
        return f"Policy '{policy}' enacted in {region}"

    def choose_policy(self, inflation, tax_revenue):
        if inflation > 1.2:
            return "tighten_compute_supply"
        elif inflation < 0.8:
            return "increase_subsidies"
        else:
            return "stable_growth"
