class GPUCitizenshipRegistry:
    def __init__(self):
        self.citizens = {}

    def issue_passport(self, user, compute_rank):
        self.citizens[user] = {
            "passport": f"GPU-{user[:4].upper()}-{compute_rank}",
            "rank": compute_rank
        }
        return self.citizens[user]
