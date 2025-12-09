class GPUStressTest:
    def simulate_crash(self, gpu_demand, crash_severity):
        return gpu_demand * (1 - crash_severity)
