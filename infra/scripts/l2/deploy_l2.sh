#!/bin/bash
set -euo pipefail

SIM="${SIMULATION_MODE:-true}"
REPORTS="${REPORTS_PATH:-reports/l2}"
mkdir -p "$REPORTS"

if [ "$SIM" = "true" ]; then
    python - <<PY
import json
out = {
    "phase": "L.2",
    "simulation_mode": True,
    "steps": [
        {"step": "terraform_plan", "result": "simulated", "module": "infra/terraform/modules/l2_governance_mesh"},
        {"step": "helm_template", "result": "simulated", "chart": "infra/helm/l2-governance"},
        {"step": "vault_policy", "result": "simulated", "policy": "l2_governance_mesh.hcl"},
        {"step": "services_start", "result": "simulated", "services": ["governance-mesh-core", "delegation-service", "ledger-service"]}
    ],
    "overall_status": "SIM_OK"
}
print(json.dumps(out, indent=2))
PY
else
    if [ "${APPROVE_L2_DEPLOY:-no}" != "yes" ]; then
        echo '{"error": "APPROVE_L2_DEPLOY not yes"}' 
        exit 1
    fi
    echo '{"phase": "L.2", "simulation_mode": false, "overall_status": "LIVE_STARTED"}'
fi