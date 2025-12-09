class OmniBrain:
    def __init__(self, world, economy, diplomacy, conflict):
        self.world = world
        self.economy = economy
        self.diplomacy = diplomacy
        self.conflict = conflict

    def decide(self):
        decisions = {}
        # if GPU resources low → boost tech
        for r in self.world.regions:
            if self.world.gpu_resources[r] < 800:
                decisions[r] = "invest_in_ai_efficiency"
            elif self.world.population[r] > 500:
                decisions[r] = "expand_infrastructure"
            else:
                decisions[r] = "normal_growth"
        return decisions
