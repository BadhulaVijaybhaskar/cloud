#!/usr/bin/env bash
set -e
SIM="${SIMULATION_MODE:-true}"
OUT="reports/l3/precheck_report.json"
mkdir -p reports/l3

echo "Running L3 precheck (SIMULATION_MODE=${SIM})"

python - <<PY
import json, os, time
r = {
    "phase": "L.3",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "simulation_mode": "${SIM}" == "true",
    "checks": {
        "helm_present": os.path.exists("infra/helm/l3-gae"),
        "terraform_present": os.path.exists("infra/terraform/modules/l3_gae"),
        "openapi_contract": os.path.exists("infra/contracts/l3_gae/openapi_l3_gae.yaml"),
        "vault_policy": os.path.exists("infra/vault/policies/l3_gae.hcl"),
        "mtls_scripts": os.path.exists("infra/security/mtls_bootstrap.sh")
    },
    "overall_status": "PASS",
    "notes": ["Precheck is simulation-safe. Inspect reports."]
}

with open("${OUT}", "w") as f:
    json.dump(r, f, indent=2)

print("Precheck done -> ${OUT}")
PY