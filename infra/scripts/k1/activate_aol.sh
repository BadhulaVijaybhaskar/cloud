#!/usr/bin/env bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
: "${APPROVE_AUTONOMY:=no}"
REPORT_DIR="reports/k1"
mkdir -p "${REPORT_DIR}"
echo "[K1] Activating Autonomous Runtime (SIM=${SIMULATION_MODE})" | tee -a "${REPORT_DIR}/activate.log"

# Deploy templates in sim mode (helm template) or live helm upgrade/install
if [ "${SIMULATION_MODE}" = "true" ]; then
  helm template aol-controller infra/helm/aol -s templates/controller.yaml > "${REPORT_DIR}/aol_controller.tpl.yaml" || true
  helm template aol-policy infra/helm/aol -s templates/policy.yaml > "${REPORT_DIR}/aol_policy.tpl.yaml" || true
  echo '{"status":"simulated-deploy"}' > "${REPORT_DIR}/deploy_summary.json"
else
  if [ "${APPROVE_AUTONOMY}" != "yes" ]; then
    echo "Approve autonomy not set. Set APPROVE_AUTONOMY=yes to proceed." >&2
    exit 2
  fi
  helm upgrade --install aol-controller infra/helm/aol --namespace "${NAMESPACE}" --wait --timeout 10m --set simulationMode=false
  helm upgrade --install aol-policy infra/helm/aol --namespace "${NAMESPACE}" --wait --timeout 10m --set simulationMode=false
  helm upgrade --install aol-executor infra/helm/aol --namespace "${NAMESPACE}" --wait --timeout 10m --set simulationMode=false
fi

# Run simulation scenarios if SIM mode
if [ "${SIMULATION_MODE}" = "true" ]; then
  # trigger simulator job
  curl -s -X POST "http://localhost:8320/v1/run-scenario" -H "Content-Type: application/json" \
    -d '{"scenario":"node-failure","duration":'${AOL_SIMULATION_DURATION:-300}'}' > "${REPORT_DIR}/simulation_job.json" || true
fi

echo "[K1] AOL activation complete (SIM=${SIMULATION_MODE})"