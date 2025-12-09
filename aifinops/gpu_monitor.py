import subprocess, json, time

def get_nvidia_smi():
    """
    Runs nvidia-smi --query-gpu and returns GPU stats.
    Works on EC2, GKE, bare metal, Docker.
    """
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=index,name,utilization.gpu,utilization.memory,memory.total,memory.used",
            "--format=csv,noheader,nounits"
        ]).decode()
    except:
        return []

    gpus = []
    for line in out.strip().split("\n"):
        idx, name, util, mem_util, mem_total, mem_used = line.split(", ")
        gpus.append({
            "index": int(idx),
            "name": name,
            "gpu_util": float(util),
            "mem_util": float(mem_util),
            "mem_total": float(mem_total),
            "mem_used": float(mem_used)
        })
    return gpus


def detect_gpu_waste(gpus):
    results = []
    for g in gpus:
        issues = []
        if g["gpu_util"] < 10:
            issues.append("GPU idle")
        if g["mem_used"] > 0 and g["gpu_util"] < 20:
            issues.append("Memory high but compute low → dataloader bottleneck")
        if g["mem_used"] == 0 and g["gpu_util"] == 0:
            issues.append("Zombie GPU → allocated but unused job")

        results.append({
            "gpu": g["index"],
            "name": g["name"],
            "issues": issues
        })
    return results


def monitor_loop(interval=30):
    """
    Continuous GPU monitor loop.
    """
    while True:
        gpus = get_nvidia_smi()
        issues = detect_gpu_waste(gpus)
        print(json.dumps(issues, indent=2))
        time.sleep(interval)
