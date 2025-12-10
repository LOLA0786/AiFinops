import random

def analyze_topology():
    """
    Fake topology: NVLink connections, PCIe lanes, multi-GPU bandwidth
    """
    return {
        "num_gpus": 8,
        "nvlink_matrix": [[random.randint(0,1) for _ in range(8)] for _ in range(8)],
        "pcie_bandwidth_gbps": random.randint(128, 256),
        "bottleneck": random.choice(["PCIe bottleneck", "NVLink imbalance", "None"])
    }
