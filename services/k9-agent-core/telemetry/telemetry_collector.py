#!/usr/bin/env python3
"""
Collect synthetic marketing metrics for FinOps simulation.
Outputs reports/k9/telemetry.json for cross-phase billing/FinOps hooks.
"""
import os
import json
import random
import time

OUT = os.getenv("REPORTS_PATH", "reports/k9")
os.makedirs(OUT, exist_ok=True)

data = {
    "phase": "K.9",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "metrics": {
        "ad_spend_usd": round(random.uniform(1000, 10000), 2),
        "impressions": random.randint(1_000_000, 5_000_000),
        "clicks": random.randint(10_000, 50_000),
        "conversions": random.randint(100, 1000),
        "cpa_usd": round(random.uniform(5, 40), 2)
    }
}
path = os.path.join(OUT, "telemetry.json")
with open(path, "w") as f:
    json.dump(data, f, indent=2)
print(f"Telemetry data written to {path}")