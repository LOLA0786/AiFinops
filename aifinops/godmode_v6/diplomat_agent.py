class AIDiplomat:
    def __init__(self, name):
        self.name = name

    def negotiate(self, partner, compute_offer, compute_request):
        if compute_request <= compute_offer * 1.2:
            return f"Agreement reached between {self.name} and {partner}"
        return f"Negotiation failed between {self.name} and {partner}"
