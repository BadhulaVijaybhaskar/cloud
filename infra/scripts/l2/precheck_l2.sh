#!/bin/bash
set -euo pipefail

SIM="${SIMULATION_MODE:-true}"
REPORTS="${REPORTS_PATH:-reports/l2}"
mkdir -p "$REPORTS"

echo "Running L.2 precheck (SIMULATION_MODE=${SIM})"

python - <<PY
import json, os
r = {
    "phase": "L.2",
    "simulation_mode": os.getenv("SIMULATION_MODE", "true"),
    "services": {},
    "integrations": {}
}

# Check services
services = ["governance-mesh-core", "delegation-service", "ledger-service", "governance-ui", "mesh-notifier"]
for s in services:
    r["services"][s] = {"exists": os.path.isdir(os.path.join("services", s))}

# Check integrations
r["integrations"]["k8_billing"] = {"available": os.path.exists("services/billing-gateway")}
r["integrations"]["k9_telemetry"] = {"available": os.path.exists("reports/k9/telemetry.json")}
r["integrations"]["l1_audit"] = {"available": os.path.exists("reports/l1/post_integration_audit.json")}

r["overall_status"] = "PASS" if all(v["exists"] for v in r["services"].values()) else "WARN"
print(json.dumps(r, indent=2))
PY