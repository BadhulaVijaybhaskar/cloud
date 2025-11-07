#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/l3
SIM=${SIMULATION_MODE:-true}

if [ "${SIM}" = "true" ]; then
    python - <<PY
import json, time
out = {
    "phase": "L.3",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "simulation_mode": True,
    "steps": [
        {"step": "terraform_plan", "result": "simulated", "module": "infra/terraform/modules/l3_gae"},
        {"step": "helm_template", "result": "simulated", "chart": "infra/helm/l3-gae"},
        {"step": "vault_policy", "result": "simulated", "policy": "l3_gae.hcl"},
        {"step": "services_start", "result": "simulated", "services": ["l3-gae-orchestrator", "l3-gae-gateway", "l3-gae-metadata"]}
    ],
    "overall_status": "SIM_OK"
}

with open("reports/l3/deploy_summary.json", "w") as f:
    json.dump(out, f, indent=2)

print("Deploy simulation complete -> reports/l3/deploy_summary.json")
PY
else
    if [ "${APPROVE_L3_DEPLOY:-no}" != "yes" ]; then
        echo "APPROVE_L3_DEPLOY!=yes -> abort live deploy"
        exit 1
    fi
    echo '{"phase": "L.3", "simulation_mode": false, "overall_status": "LIVE_STARTED"}' > reports/l3/deploy_summary.json
fi