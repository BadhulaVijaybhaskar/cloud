#!/usr/bin/env python3
import requests, json, os, time
from datetime import datetime
OUT = "reports"
os.makedirs(OUT, exist_ok=True)

services = {
  "predictive": "http://localhost:8010/healthz",
  "analytics": "http://localhost:8020/healthz"
}
results = {"timestamp": datetime.utcnow().isoformat()+"Z", "latencies":{}}

for n,u in services.items():
  t0 = time.time()
  try:
    r = requests.get(u, timeout=2)
    results["latencies"][n] = {
      "status": r.status_code,
      "latency_ms": round((time.time()-t0)*1000,2)
    }
  except Exception as e:
    results["latencies"][n] = {"status": "down", "error": str(e)}

with open(os.path.join(OUT,"PhaseC_PerfSummary.json"),"w") as fh:
  json.dump(results, fh, indent=2)
print(json.dumps(results, indent=2))