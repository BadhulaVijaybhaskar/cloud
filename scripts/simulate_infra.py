#!/usr/bin/env python3
# scripts/simulate_infra.py
import json
import os
import socket
from datetime import datetime

OUT_DIR = "reports"
os.makedirs(OUT_DIR, exist_ok=True)

services = {
    "vault": os.environ.get("VAULT_ADDR", None),
    "prometheus": os.environ.get("PROM_URL", None),
    "s3": os.environ.get("S3_ENDPOINT", None),
    "postgres": os.environ.get("POSTGRES_DSN", None),
    "cosign": None  # cosign binary presence will be checked
}

def check_port(url):
    # naive: treat as host:port if contains :
    if not url:
        return False
    try:
        if "://" in url:
            host = url.split("://",1)[1].split("/")[0]
        else:
            host = url
        if ":" in host:
            h,p = host.split(":",1)
            s = socket.socket()
            s.settimeout(1.0)
            s.connect((h, int(p)))
            s.close()
            return True
        return False
    except Exception:
        return False

def check_cosign():
    from shutil import which
    return which("cosign") is not None

results = {}
for name, url in services.items():
    if name == "cosign":
        ok = check_cosign()
        results[name] = {"available": ok, "note": "cosign binary on PATH" if ok else "not found"}
    else:
        ok = check_port(url) if url else False
        results[name] = {"available": ok, "endpoint": url or "<unset>"}
        if not ok:
            results[name]["mode"] = "SIMULATED"

summary = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "results": results
}

with open(os.path.join(OUT_DIR, "PhaseB_InfraSimulation.log"), "w") as fh:
    fh.write("Phase B Infra Simulation\n")
    fh.write(json.dumps(summary, indent=2))

with open(os.path.join(OUT_DIR, "phaseB_prereqs_simulation.json"), "w") as fh:
    json.dump(summary, fh, indent=2)

print("Simulation complete. Outputs:")
print(" -", os.path.join(OUT_DIR, "PhaseB_InfraSimulation.log"))
print(" -", os.path.join(OUT_DIR, "phaseB_prereqs_simulation.json"))
