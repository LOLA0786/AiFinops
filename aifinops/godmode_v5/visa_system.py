class GPUVisaSystem:
    def __init__(self):
        self.visas = {}

    def request_visa(self, user, region, compute_needed):
        visa_id = f"VS-{user[:3]}-{region[:3]}"
        self.visas[visa_id] = {
            "user": user,
            "region": region,
            "compute_needed": compute_needed
        }
        return visa_id
