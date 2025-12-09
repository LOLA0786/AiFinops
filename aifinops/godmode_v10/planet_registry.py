class PlanetRegistry:
    def __init__(self):
        self.planets = {}
    def register(self, name, resources, latency):
        self.planets[name] = {"resources": resources, "latency": latency}
    def list_planets(self):
        return self.planets
