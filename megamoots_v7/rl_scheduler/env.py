class RLSchedulerEnv:
    """Environment scaffold for RL-based GPU scheduling."""
    def step(self, action):
        return {"reward": 1.0}, False
