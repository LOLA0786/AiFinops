import random

class GPUWorld:
    def __init__(self):
        self.regions = ["AWSland", "GCPia", "Azureon", "CoreWeavia", "LambdaRealm"]
        self.population = {r: random.randint(50, 200) for r in self.regions}
        self.gpu_resources = {r: random.randint(1000, 5000) for r in self.regions}
        self.tech_level = {r: random.uniform(1.0, 5.0) for r in self.regions}

    def tick(self):
        # population grows with tech level
        for r in self.regions:
            self.population[r] += int(self.population[r] * (self.tech_level[r] / 100))
            self.gpu_resources[r] -= self.population[r] // 5
