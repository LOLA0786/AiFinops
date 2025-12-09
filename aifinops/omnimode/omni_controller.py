class OmniController:
    def __init__(self, brain, simulation):
        self.brain = brain
        self.simulation = simulation

    def run_cycle(self):
        decisions = self.brain.decide()
        gdp = self.simulation.step()
        return {"decisions": decisions, "gdp": gdp}
