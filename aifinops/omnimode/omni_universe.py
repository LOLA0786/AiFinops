from aifinops.godmode_v8.world_generator import GPUWorld
from aifinops.godmode_v8.economy_engine import GPUEconomyEngine
from aifinops.godmode_v8.diplomacy_engine import GPUDiplomacyEngine
from aifinops.godmode_v8.conflict_engine import GPUConflictEngine
from aifinops.godmode_v8.simulation_engine import GPUSimulationEngine
from aifinops.omnimode.omni_brain import OmniBrain

class OmniUniverse:
    def __init__(self):
        self.world = GPUWorld()
        self.economy = GPUEconomyEngine()
        self.diplomacy = GPUDiplomacyEngine()
        self.conflict = GPUConflictEngine()
        self.simulation = GPUSimulationEngine(
            self.world, self.economy, self.diplomacy, self.conflict
        )
        self.brain = OmniBrain(self.world, self.economy, self.diplomacy, self.conflict)

    def tick(self):
        return self.simulation.step()
