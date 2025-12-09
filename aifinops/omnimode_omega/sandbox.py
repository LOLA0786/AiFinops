import copy
class SandboxedExecutor:
    def __init__(self):
        self.state = {}
    def run_patch(self, patch_func):
        # patch_func receives a deepcopy of state, returns new state or diff
        state_copy = copy.deepcopy(self.state)
        new_state = patch_func(state_copy)
        if isinstance(new_state, dict):
            self.state = new_state
            return True
        return False
