#!/usr/bin/env python3
# scripts/generate_phase_snapshot.py
# Produce a simple JSON snapshot of current git HEAD and reports list.

import json,subprocess,glob,os
out={}
try:
    sha = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
except Exception:
    sha = "NO_GIT"
out["commit"] = sha
out["reports"] = sorted(glob.glob("reports/*.md") + glob.glob("reports/*.json"))
out["generated_at"] = subprocess.check_output(["date","-u","+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
open("reports/PhaseG.2_Snapshot.json","w").write(json.dumps(out, indent=2))
print("Wrote reports/PhaseG.2_Snapshot.json")