class GPUConflictEngine:
    def __init__(self):
        pass

    def compute_war_outcome(self, attacker, defender, attacker_power, defender_power):
        ratio = attacker_power / defender_power
        if ratio > 1.2:
            return f"{attacker} conquers {defender}"
        elif ratio < 0.8:
            return f"{defender} repels attack from {attacker}"
        else:
            return f"Stalemate between {attacker} and {defender}"
