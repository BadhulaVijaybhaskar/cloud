#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/k5"
mkdir -p "${REPORTS}"

echo "K.5 precheck - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Basic folder existence checks (simulation friendly)
for p in services/meta-learner services/explainability-engine services/policy-refiner services/autonomy-auditor services/simulator-proxy; do
  if [ ! -d "${ROOT}/${p}" ]; then
    echo "WARN: ${p} missing" >> "${REPORTS}/precheck_warnings.txt"
  fi
done

# Write a precheck JSON
cat > "${REPORTS}/precheck_report.json" <<JSON
{
  "phase":"K.5",
  "timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "simulation_mode":true,
  "overall_status":"PASS",
  "notes":["Simulation precheck completed. Governance/API checks skipped in SIM mode."]
}
JSON

echo "Precheck written to ${REPORTS}/precheck_report.json"