class GPUIMF:
    def __init__(self):
        self.programs = {}

    def stabilization_program(self, region, deficit):
        amount = deficit * 1.5
        self.programs[region] = amount
        return amount
