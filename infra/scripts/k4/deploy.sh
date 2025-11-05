#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${ROOT}/reports/k4"
mkdir -p "${REPORTS_DIR}"
SIM=${SIMULATION_MODE:-true}

echo "K.4 deploy - SIMULATION_MODE=${SIM}"

# terraform plan (simulated)
echo '{"step":"terraform_plan","result":"simulated"}' > "${REPORTS_DIR}/deploy_summary.json"
# helm template rendering (simulated)
echo '{"step":"helm_template","result":"simulated"}' >> "${REPORTS_DIR}/deploy_summary.json"

# Seed example experience artifact (simulation)
cat > "${REPORTS_DIR}/transfer_log.json" <<'JSON'
[]
JSON

echo '{"phase":"K.4","simulation_mode":true,"overall_status":"SIM_OK"}' >> "${REPORTS_DIR}/deploy_summary.json"
echo "Deploy (simulation) wrote ${REPORTS_DIR}/deploy_summary.json and transfer_log.json"