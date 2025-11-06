#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_DIR="${ROOT}/reports/k6"
mkdir -p "${REPORT_DIR}"

SIMULATION_MODE=${SIMULATION_MODE:-true}
APPROVE=${APPROVE_K6_DEPLOY:-no}

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
RUN_ID="k6-deploy-$(date -u +%Y%m%dT%H%M%SZ)"

echo "K.6 deploy: RUN_ID=${RUN_ID} SIMULATION_MODE=${SIMULATION_MODE} APPROVE=${APPROVE}"

# run precheck first
SIMULATION_MODE=${SIMULATION_MODE} ./infra/scripts/k6/precheck_k6.sh

# Terraform plan (simulated)
echo "Rendering terraform plan (simulated)"
mkdir -p "${REPORT_DIR}"
cat > "${REPORT_DIR}/terraform_plan_k6.json" <<JSON
{"module":"infra/terraform/modules/k6_integration","plan":{"to_create":2,"to_change":0,"to_destroy":0}}
JSON

# Helm template render (simulated)
cat > "${REPORT_DIR}/helm_template_k6.yaml" <<YAML
# Simulated helm render for k6 integration
apiVersion: v1
kind: List
items: []
YAML

# Deploy step — simulation guard
if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "SIMULATION_MODE=true - skipping live apply. Writing simulated boot artifacts..."
  cat > "${REPORT_DIR}/k6_deploy_summary.json" <<JSON
{"run_id":"${RUN_ID}","status":"SIMULATION_OK","timestamp":"${TS}","notes":["No live changes performed - simulation only"]}
JSON
  echo "Deploy simulated. Check ${REPORT_DIR}/k6_deploy_summary.json"
  exit 0
fi

# Live path - gated
if [ "${APPROVE}" != "yes" ]; then
  echo "APPROVE_K6_DEPLOY is not 'yes'. Aborting live deploy."
  exit 2
fi

# (Live apply - operator only)
terraform -chdir="${ROOT}/infra/terraform/modules/k6_integration" init -input=false
terraform -chdir="${ROOT}/infra/terraform/modules/k6_integration" apply -auto-approve
helm upgrade --install k6-integration "${ROOT}/infra/helm/k6-integration"
echo '{"status":"LIVE_APPLIED"}' > "${REPORT_DIR}/k6_deploy_summary.json"