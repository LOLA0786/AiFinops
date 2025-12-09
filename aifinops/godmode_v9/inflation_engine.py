class GPUInflationEngine:
    def __init__(self):
        self.inflation = 1.0

    def adjust(self, supply, demand):
        if demand > supply:
            self.inflation += 0.05
        elif supply > demand:
            self.inflation -= 0.03
        return round(self.inflation, 3)
