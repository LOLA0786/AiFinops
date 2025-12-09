class RuleEngine:
    def __init__(self):
        self.rules = []
    def add_rule(self, rule):
        # rule = {"id":..., "cond": callable, "action": callable}
        self.rules.append(rule)
    def evaluate(self, context):
        for r in self.rules:
            if r["cond"](context):
                r["action"](context)
