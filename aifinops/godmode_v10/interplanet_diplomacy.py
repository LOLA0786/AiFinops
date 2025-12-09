class InterplanetDiplomacy:
    def __init__(self):
        self.treaties = {}
    def sign_treaty(self, p1, p2, terms):
        key = f"{p1}-{p2}"
        self.treaties[key] = terms
    def get_treaty(self, p1, p2):
        return self.treaties.get(f"{p1}-{p2}")
