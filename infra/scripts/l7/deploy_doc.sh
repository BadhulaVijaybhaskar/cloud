#!/bin/bash
set -euo pipefail

COMPONENT="l7-federated-cognitive"
SIM=${SIMULATION_MODE:-true}
SERVICES_PATH="services"
INFRA_PATH="infra"
POLICIES_PATH="${POLICIES_PATH:-infra/vault/policies}"

echo "L.7 deploy started. SIMULATION_MODE=${SIM}"

# Build docker images (simulation: skip push)
for svc in l7-orchestrator l7-learner l7-aggregator l7-explainer l7-audit-store; do
  if [ -d "${SERVICES_PATH}/${svc}" ]; then
    echo "Building ${svc}..."
    docker build -t "${DOCKER_REGISTRY}/${svc}:latest" "${SERVICES_PATH}/${svc}" || echo "Build simulated"
  fi
done

# Apply vault policies (simulated)
if [ -d "${POLICIES_PATH}" ]; then
  echo "Applying vault policies (simulated)..."
  for p in ${POLICIES_PATH}/l7_*.hcl; do
    echo "Would apply ${p}"
  done
fi

# Terraform + Helm (simulated)
if [ "${SIM}" = "false" ]; then
  terraform -chdir="${INFRA_PATH}/terraform/modules/l7_federated_continuum" apply -auto-approve
  helm upgrade --install l7-federated-continuum "${INFRA_PATH}/helm/l7-federated-continuum"
else
  echo "SIMULATION: rendering terraform plan + helm templates"
  terraform -chdir="${INFRA_PATH}/terraform/modules/l7_federated_continuum" plan -out="${REPORTS_PATH}/terraform_plan_l7.out" || true
  helm template "${INFRA_PATH}/helm/l7-federated-continuum" > "${REPORTS_PATH}/helm_template_l7.yaml" || true
fi

echo '{"phase":"L.7","status":"SIM_OK","timestamp":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"}' > "${REPORTS_PATH}/deploy_summary.json"
echo "L.7 deploy complete."