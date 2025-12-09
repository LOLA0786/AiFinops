class MetaAgent:
    def __init__(self, name):
        self.name = name
        self.ideas = []
    def propose_change(self, change_desc):
        self.ideas.append(change_desc)
        return {"agent": self.name, "proposal": change_desc}
    def list_proposals(self):
        return self.ideas
