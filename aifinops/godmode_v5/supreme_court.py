class GPUSupremeCourt:
    def resolve(self, dispute):
        # naive resolution: favor provider when conflict is unclear
        if dispute.get("type") == "pricing":
            return "Ruling: Provider allowed dynamic repricing."
        elif dispute.get("type") == "rights":
            return "Ruling: User granted GPU usage extension."
        return "Ruling: Case dismissed."
