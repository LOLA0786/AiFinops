class GPUSanctions:
    def __init__(self):
        self.blocked = {}

    def sanction(self, ai_name, severity):
        self.blocked[ai_name] = severity

    def is_sanctioned(self, ai_name):
        return ai_name in self.blocked
