#!/bin/bash
set -e
SIM=${SIMULATION_MODE:-true}
echo "Simulated deploy (SIMULATION_MODE=${SIM})"
mkdir -p reports/l4

python - <<PY
import json, time
out = {
    "phase": "L.4",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "simulation_mode": "${SIM}" == "true",
    "steps": [
        {"step": "terraform_plan", "result": "simulated"},
        {"step": "helm_template", "result": "simulated"},
        {"step": "services_deploy", "result": "simulated"}
    ],
    "status": "SIM_OK"
}

with open("reports/l4/deploy_summary.json", "w") as f:
    json.dump(out, f, indent=2)

print("L.4 deploy summary written to reports/l4/deploy_summary.json")
PY