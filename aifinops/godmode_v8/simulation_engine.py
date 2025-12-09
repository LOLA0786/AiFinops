from random import choice, uniform

class GPUSimulationEngine:
    def __init__(self, world, economy, diplomacy, conflict):
        self.world = world
        self.economy = economy
        self.diplomacy = diplomacy
        self.conflict = conflict

    def step(self):
        # evolve tech
        for r in self.world.regions:
            self.world.tech_level[r] += uniform(-0.05, 0.1)

        # evaluate economy
        gdp = self.economy.calculate_gdp(
            self.world.population, self.world.tech_level, self.world.gpu_resources
        )

        # random conflicts
        if uniform(0, 1) < 0.15:
            a = choice(self.world.regions)
            b = choice([x for x in self.world.regions if x != a])
            print(self.conflict.compute_war_outcome(a, b, gdp[a], gdp[b]))

        return gdp
