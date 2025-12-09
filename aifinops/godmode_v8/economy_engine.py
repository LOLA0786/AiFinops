class GPUEconomyEngine:
    def __init__(self):
        self.gdp = {}

    def calculate_gdp(self, population, tech_level, gpu_resources):
        gdp = {}
        for region in population:
            gdp[region] = (population[region] * tech_level[region]) + (gpu_resources[region] * 0.5)
        self.gdp = gdp
        return gdp
