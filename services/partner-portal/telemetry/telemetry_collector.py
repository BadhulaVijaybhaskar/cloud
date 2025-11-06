#!/usr/bin/env python3
"""
Telemetry collector stub for Partner Portal.
Generates a sample reports/k7/telemetry.json when run with --sample.
Designed for SIMULATION_MODE usage.
"""
import json
import argparse
import random
import time
from pathlib import Path

def sample_telemetry():
    now = int(time.time())
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "partner_metrics": [
            {"partner_id": "partner-test-1", "requests": random.randint(50,200), "errors": random.randint(0,5)},
            {"partner_id": "partner-test-2", "requests": random.randint(20,120), "errors": random.randint(0,3)},
            {"partner_id": "partner-test-3", "requests": random.randint(5,80), "errors": random.randint(0,2)}
        ],
        "summary": {
            "total_requests": 0,
            "total_errors": 0
        }
    }

def compute_summary(data):
    total_requests = sum(p["requests"] for p in data["partner_metrics"])
    total_errors = sum(p["errors"] for p in data["partner_metrics"])
    data["summary"]["total_requests"] = total_requests
    data["summary"]["total_errors"] = total_errors
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="reports/k7/telemetry.json")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    if args.sample:
        data = sample_telemetry()
        data = compute_summary(data)
        with open(args.out, "w") as f:
            json.dump(data, f, indent=2)
        print("Wrote sample telemetry to", args.out)
    else:
        print("No operation in telemetry stub (use --sample)")

if __name__ == "__main__":
    main()