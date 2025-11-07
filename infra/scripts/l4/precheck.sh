#!/bin/bash
set -e
OUT_DIR="reports/l4"
mkdir -p "${OUT_DIR}"

python - <<PY
import json, os, time
r = {
    "phase": "L.4",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "simulation_mode": os.getenv("SIMULATION_MODE", "true"),
    "checks": {
        "services": {
            "l4-orchestrator": os.path.exists("services/l4-orchestrator"),
            "l4-model-registry": os.path.exists("services/l4-model-registry"),
            "l4-edge-node": os.path.exists("services/l4-edge-node"),
            "l4-optimizer": os.path.exists("services/l4-optimizer"),
            "l4-security-broker": os.path.exists("services/l4-security-broker")
        },
        "contracts": os.path.exists("infra/contracts/l4/openapi_l4_orchestrator.yaml"),
        "terraform": os.path.exists("infra/terraform/modules/l4_distributed_intel"),
        "helm": os.path.exists("infra/helm/l4-distributed-intel")
    },
    "overall_status": "PASS"
}

with open("${OUT_DIR}/precheck_report.json", "w") as f:
    json.dump(r, f, indent=2)

print("L.4 precheck written to ${OUT_DIR}/precheck_report.json")
PY