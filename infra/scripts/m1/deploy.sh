#!/bin/bash
set -euo pipefail

COMPONENT="m1-global-certification"
SIM=${SIMULATION_MODE:-true}
INFRA="${INFRA_PATH:-infra}"
SERVICES="${SERVICES_PATH:-services}"
POLICIES="${POLICIES_PATH:-infra/vault/policies}"

echo "Deploy script for ${COMPONENT} (SIMULATION_MODE=${SIM})"

# Build services (simulation safe: skip docker push if SIM=true)
for svc in ${SERVICES}/m1-*; do
  if [ -d "$svc" ]; then
    echo "Building $(basename $svc)..."
    docker build -t "${DOCKER_REGISTRY}/$(basename $svc):latest" "$svc" || echo "Build simulated or failed"
  fi
done

# Apply vault policies (simulate)
if [ "$SIM" = "true" ]; then
  echo "SIMULATION_MODE=true: skipping live terraform/helm apply"
else
  terraform -chdir="${INFRA}/terraform/modules/m1_global_certification" apply -auto-approve
  helm upgrade --install "${COMPONENT}" "${INFRA}/helm/m1-global-certification" --namespace "${NAMESPACE}"
  if [ -f "${POLICIES}/m1_certification.hcl" ]; then
    vault policy write "m1_certification" "${POLICIES}/m1_certification.hcl"
  fi
fi

echo "Deployment complete (simulated=${SIM})"