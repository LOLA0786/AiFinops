from aifinops.godmode_v8.world_generator import GPUWorld
from aifinops.godmode_v8.economy_engine import GPUEconomyEngine
from aifinops.godmode_v8.conflict_engine import GPUConflictEngine
from aifinops.godmode_v8.diplomacy_engine import GPUDiplomacyEngine
from aifinops.godmode_v8.simulation_engine import GPUSimulationEngine

from aifinops.godmode_v9.tax_engine import GPUTaxEngine
from aifinops.godmode_v9.inflation_engine import GPUInflationEngine
from aifinops.godmode_v9.governance_engine import GPUGovernanceEngine
from aifinops.godmode_v9.economy_loop import PlanetaryEconomyLoop

class OmniModeUltra:
    def __init__(self):
        # world
        self.world = GPUWorld()
        self.economy = GPUEconomyEngine()
        self.conflict = GPUConflictEngine()
        self.diplomacy = GPUDiplomacyEngine()

        # planet-scale engines
        self.tax_engine = GPUTaxEngine()
        self.inflation_engine = GPUInflationEngine()
        self.governance_engine = GPUGovernanceEngine()

        # simulation
        self.sim = GPUSimulationEngine(
            self.world, self.economy, self.diplomacy, self.conflict
        )
        self.planet = PlanetaryEconomyLoop(
            self.world,
            self.economy,
            self.tax_engine,
            self.inflation_engine,
            self.governance_engine
        )

    def run_cycle(self):
        sim_result = self.sim.step()
        eco_result = self.planet.tick()
        return {
            "simulation": sim_result,
            "planetary_economy": eco_result
        }
