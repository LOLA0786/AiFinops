"""
Agent daemon scaffold: runs collectors and uploads telemetry.
"""
import time
from agent.collectors.sample import sample_metrics
from agent.uploader.httpuploader import upload

def main_loop():
    while True:
        data = sample_metrics()
        upload(data)
        time.sleep(5)

if __name__=="__main__":
    main_loop()
