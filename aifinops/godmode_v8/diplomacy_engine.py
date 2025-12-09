class GPUDiplomacyEngine:
    def __init__(self):
        self.relations = {}

    def set_relation(self, a, b, status):
        self.relations[(a,b)] = status

    def improve_relations(self, a, b):
        self.relations[(a,b)] = "allied"
        return f"{a} and {b} are now allies."

    def worsen_relations(self, a, b):
        self.relations[(a,b)] = "hostile"
        return f"{a} and {b} are now hostile."
