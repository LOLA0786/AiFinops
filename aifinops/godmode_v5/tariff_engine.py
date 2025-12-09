class GPUTariffEngine:
    def __init__(self):
        self.tariffs = {}

    def set_tariff(self, from_region, to_region, percent):
        self.tariffs[(from_region, to_region)] = percent

    def calculate_cost(self, from_region, to_region, cost):
        key = (from_region, to_region)
        rate = self.tariffs.get(key, 0)
        return cost + (cost * rate / 100)
