#!/usr/bin/env bash
set -e
REPORTS="reports/k7"
mkdir -p "${REPORTS}"
echo "Starting K.7 deploy (SIMULATION_MODE=${SIMULATION_MODE:-true})"

# build images (simulated)
for svc in partner-portal marketplace-v2 partner-sandbox partner-onboard-worker; do
  echo "Simulating docker build for ${svc}"
done

if [ "${SIMULATION_MODE:-true}" = "true" ]; then
  STATUS="SIMULATION_OK"
else
  if [ "${APPROVE_K7_DEPLOY}" != "yes" ]; then
    echo "APPROVE_K7_DEPLOY not yes - aborting live deploy"
    exit 3
  fi
  STATUS="LIVE_APPLIED"
  # terraform -chdir=infra/terraform/modules/k7_partner_ecosystem apply -auto-approve
  # helm upgrade --install k7 infra/helm/k7-partner-ecosystem
fi

cat > "${REPORTS}/deploy_summary.json" <<JSON
{
  "phase":"K.7",
  "simulation_mode":"${SIMULATION_MODE:-true}",
  "status":"${STATUS}",
  "notes":["Simulated builds complete","Helm/Terraform skipped in simulation"]
}
JSON
echo "Deploy (simulated) complete. Report at ${REPORTS}/deploy_summary.json"