# Simple load test using requests for local emulation
import requests
import time

PRED_URL = "http://localhost:8500/v1/forecast"
ITER = 50

def run_load():
    for i in range(ITER):
        try:
            r = requests.post(PRED_URL, json={"target": f"web-{i%4}"}, timeout=2)
            print(i, r.status_code, r.text[:80])
        except Exception as e:
            print("error", e)
        time.sleep(0.1)

if __name__ == "__main__":
    run_load()