import time, subprocess, json

def get_gpu_util():
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"]
        ).decode()
        util, mem = output.strip().split(",")
        return int(util), int(mem)
    except:
        return 0, 0

while True:
    util, mem = get_gpu_util()

    if util < 10:
        print("GPU idle → scaling down...")
        # Future: call AWS/GCP to shrink node group
    else:
        print("GPU busy.")

    time.sleep(30)
