from random import randint

class PlanetaryEconomyLoop:
    def __init__(self, world, economy, tax_engine, inflation_engine, governance_engine):
        self.world = world
        self.economy = economy
        self.tax_engine = tax_engine
        self.inflation_engine = inflation_engine
        self.governance = governance_engine

    def tick(self):
        gdp = self.economy.calculate_gdp(
            self.world.population, 
            self.world.tech_level, 
            self.world.gpu_resources
        )
        tax = self.tax_engine.collect(gdp)
        inflation = self.inflation_engine.adjust(
            supply=sum(self.world.gpu_resources.values()),
            demand=sum(self.world.population.values()) * randint(1, 3)
        )
        policy = self.governance.choose_policy(inflation, tax)

        return {
            "gdp": gdp,
            "tax": tax,
            "inflation": inflation,
            "policy": policy
        }
