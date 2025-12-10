from megamoots_v7.rl_scheduler.rl_policy import RLSchedulerPolicy
from megamoots_v7.predictive_maintenance.predictor import FailurePredictor
from megamoots_v7.gpu_marketplace.broker import GPUMarketBroker
from megamoots_v7.topology_analyzer.analyzer import TopologyAnalyzer
from megamoots_v7.auto_heal.controller import AutoHealController

print("=== MegaMoats v7 Demo ===")
print("RL scheduler:", RLSchedulerPolicy().predict({}))
print("Failure risk:", FailurePredictor().predict_failure_risk({}))
print("Best provider:", GPUMarketBroker().choose_best_provider())
print("Topology:", TopologyAnalyzer().analyze())
print("Auto-heal:", AutoHealController().run())
