class WormholeRouter:
    def __init__(self):
        self.links = {}  # (from,to)->bandwidth
    def open_link(self, a, b, bw):
        self.links[(a,b)] = bw
    def route(self, from_p, to_p, size):
        # naive: check direct capacity
        cap = self.links.get((from_p,to_p), 0)
        return {"ok": cap >= size, "capacity": cap}
