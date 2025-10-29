import json,glob,subprocess,os
sha="NO_GIT"
try: sha=subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
except Exception: pass
out={"commit":sha,"reports":sorted(glob.glob("reports/H.3*"))}
os.makedirs("reports",exist_ok=True)
open("reports/PhaseH.3_Snapshot.json","w").write(json.dumps(out,indent=2))
print("Snapshot written")