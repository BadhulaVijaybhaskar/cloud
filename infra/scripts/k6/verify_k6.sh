#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_DIR="${ROOT}/reports/k6"
mkdir -p "${REPORT_DIR}"

SIMULATION_MODE=${SIMULATION_MODE:-true}
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "K.6 verify: SIMULATION_MODE=${SIMULATION_MODE}"

# Basic health aggregation
python3 - <<PY
import json, os, requests
rfile = os.path.join("${REPORT_DIR}", "k6_compatibility_report.json")
if os.path.exists(rfile):
    with open(rfile) as f:
        data = json.load(f)
else:
    data = {"checks":{}}
data["verification"] = {"timestamp":"${TS}","sim":${str(SIMULATION_MODE).lower()}}
with open(os.path.join("${REPORT_DIR}","k6_verification_summary.json"),"w") as f:
    json.dump(data, f, indent=2)
print("Wrote", os.path.join("${REPORT_DIR}","k6_verification_summary.json"))
PY