#!/usr/bin/env python3
# scripts/generate_phase_snapshot.py
import json
import os
import subprocess
from datetime import datetime

OUT_DIR = "reports"
os.makedirs(OUT_DIR, exist_ok=True)

def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return None

def list_reports():
    files = []
    for root, _, filenames in os.walk("reports"):
        for f in filenames:
            files.append(os.path.join(root, f))
    return sorted(files)

snapshot = {
    "phase": "B",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "git_commit": git_commit(),
    "reports_found": list_reports()
}

out_path = os.path.join(OUT_DIR, "PhaseB_Snapshot.json")
with open(out_path, "w") as fh:
    json.dump(snapshot, fh, indent=2)

print("Snapshot written:", out_path)
