#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${ROOT}/reports/k4"
mkdir -p "${REPORTS_DIR}"

echo "K.4 precheck - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Check required folders
for p in services/experience-repository services/cognitive-learner services/transfer-agent services/optimizer-proxy; do
  if [ ! -d "$ROOT/$p" ]; then
    echo "WARN: missing $p (expected for skeleton in simulation)" >> "${REPORTS_DIR}/precheck_report.json"
  fi
done

# Check governance API reachability (simulation: skip)
if [ "${SIMULATION_MODE}" = "true" ]; then
  echo '{"phase":"K.4","simulation_mode":true,"overall_status":"PASS","notes":["Simulation: governance/API checks skipped"]}' > "${REPORTS_DIR}/precheck_report.json"
  echo "Precheck (simulation) written to ${REPORTS_DIR}/precheck_report.json"
  exit 0
fi

# Live checks (only executed when SIMULATION_MODE=false)
# - governance api
curl -fsS "http://governance-api:8400/health" >/dev/null || { echo "Governance API not reachable"; exit 2; }
# - vault policy existence
# (Add vault cli checks)
echo '{"phase":"K.4","simulation_mode":false,"overall_status":"PASS"}' > "${REPORTS_DIR}/precheck_report.json"