class GPUDiplomaticEmbassy:
    def __init__(self):
        self.relationships = {}

    def set_relation(self, ai1, ai2, status):
        self.relationships[(ai1, ai2)] = status

    def get_relation(self, ai1, ai2):
        return self.relationships.get((ai1, ai2), "neutral")
