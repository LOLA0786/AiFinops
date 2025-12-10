"""
Synthetic GPU Cluster Simulator
- Generates telemetry, training logs, and market signals
- Stores outputs under sim/output for local consumption
"""
import os, time, json, random, threading

OUT_DIR = "sim/output"
os.makedirs(OUT_DIR, exist_ok=True)

def telemetry_stream(node_count=3, gpus_per_node=1, interval=0.2, total_samples=200):
    rng = random.Random(0)
    path = os.path.join(OUT_DIR, "telemetry.jsonl")
    with open(path,"w") as f:
        for t in range(total_samples):
            for n in range(node_count):
                for g in range(gpus_per_node):
                    sample = {
                        "node": f"node-{n}",
                        "gpu_index": g,
                        "gpu_util": max(0, min(100, int(rng.gauss(60,20)))),
                        "mem_used": int(abs(rng.gauss(12000,2000))),
                        "mem_total": 32768,
                        "ts": int(time.time())
                    }
                    f.write(json.dumps(sample)+"\\n")
            time.sleep(interval)

def training_log_generator(num_jobs=5, lines_per_job=100):
    path = os.path.join(OUT_DIR, "training_logs.txt")
    rng = random.Random(1)
    with open(path,"w") as f:
        for j in range(num_jobs):
            bs = rng.choice([2,4,8,16,32])
            for l in range(lines_per_job):
                if rng.random() < 0.01:
                    f.write("CUDA out of memory at step %d\\n"%l)
                if rng.random() < 0.02:
                    f.write("DataLoader warning: slow worker\\n")
                f.write(f"Job {j} epoch {l} batch_size={bs}\\n")

def market_signal_generator(intervals=50):
    path = os.path.join(OUT_DIR, "market_signals.jsonl")
    rng = random.Random(2)
    with open(path,"w") as f:
        base = {"aws":3.2,"gcp":2.9,"azure":3.5}
        for i in range(intervals):
            for cloud,p in base.items():
                # small jitter and occasional spike
                price = p * (1 + rng.gauss(0,0.05))
                if rng.random() < 0.02:
                    price *= 1 + rng.uniform(0.5,1.5)
                f.write(json.dumps({"ts":int(time.time()),"cloud":cloud,"price":round(price,3)})+"\\n")
            time.sleep(0.05)

def run_all():
    t1 = threading.Thread(target=telemetry_stream, kwargs={"total_samples":400})
    t2 = threading.Thread(target=training_log_generator)
    t3 = threading.Thread(target=market_signal_generator)
    t1.start(); t2.start(); t3.start()
    t1.join(); t2.join(); t3.join()
    print("Simulator finished. Output in sim/output")

if __name__ == "__main__":
    run_all()
