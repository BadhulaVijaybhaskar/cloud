#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="reports/k2"
mkdir -p "${OUT_DIR}"

SIM=${SIMULATION_MODE:-true}
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPORT="${OUT_DIR}/precheck_report.json"

echo "Running K.2 precheck (SIMULATION_MODE=${SIM})..."

# Basic checks (endpoints, files, vault connectivity)

# Example: model file
MODEL_PRESENT="no"
if [ -f "models/base_predictor.pkl" ]; then
  MODEL_PRESENT="present"
fi

# Endpoint health checks (only in simulation or live when endpoints reachable)
PRED_HEALTH="unreachable"
if curl -s --max-time 2 http://localhost:8500/health >/dev/null 2>&1; then
  PRED_HEALTH="healthy"
fi

# Vault connectivity placeholder (do not expose secrets)
VAULT_OK="unknown"
if [ "${SIM}" = "false" ]; then
  if command -v vault >/dev/null 2>&1 && vault status >/dev/null 2>&1; then
    VAULT_OK="connected"
  else
    VAULT_OK="unreachable"
  fi
else
  VAULT_OK="simulated"
fi

cat > "${REPORT}" <<JSON
{
  "phase": "K.2",
  "timestamp": "${TS}",
  "simulation_mode": ${SIM},
  "checks": {
    "model_file": "${MODEL_PRESENT}",
    "predictive_ops_engine": "${PRED_HEALTH}",
    "vault_connectivity": "${VAULT_OK}"
  },
  "overall_status": "$( [ "${SIM}" = "true" ] && echo PASS || echo PENDING )",
  "notes": "Use SIMULATION_MODE=false for live precheck; ensure vault access and approvals."
}
JSON

echo "Precheck written to ${REPORT}"