#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/l3
SIM=${SIMULATION_MODE:-true}

python - <<PY
import json, os, time
r = {
    "phase": "L.3",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "simulation_mode": "${SIM}",
    "checks": {
        "contracts": os.path.exists("infra/contracts/l3_gae/openapi_l3_gae.yaml"),
        "terraform_module": os.path.exists("infra/terraform/modules/l3_gae"),
        "helm_chart": os.path.exists("infra/helm/l3-gae"),
        "vault_policy": os.path.exists("infra/vault/policies/l3_gae.hcl")
    },
    "services": {}
}

services = ["l3-gae-orchestrator", "l3-gae-gateway", "l3-gae-metadata", "l3-gae-bus", "l3-gae-auditor"]
for s in services:
    r["services"][s] = {"exists": os.path.isdir(os.path.join("services", s))}

r["overall_status"] = "PASS" if all(r["checks"].values()) else "WARN"

with open("reports/l3/precheck_report.json", "w") as f:
    json.dump(r, f, indent=2)

print("Precheck complete -> reports/l3/precheck_report.json")
PY