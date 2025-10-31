#!/usr/bin/env python3
import json,glob,subprocess,os
out={}
try:
    sha=subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
except Exception:
    sha="NO_GIT"
out["commit"]=sha
out["reports"]=sorted(glob.glob("reports/*.md")+glob.glob("reports/*.json"))
try:
    out["generated_at"]=subprocess.check_output(["date","-u","+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
except:
    import datetime
    out["generated_at"]=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
with open("reports/PhaseI.7_Snapshot.json","w") as f:
    f.write(json.dumps(out,indent=2))
print("Wrote reports/PhaseI.7_Snapshot.json")