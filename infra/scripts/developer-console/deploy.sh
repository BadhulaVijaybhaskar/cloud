#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
COMP="developer-console"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
IMAGE_TAG="${IMAGE_TAG:-j2-dev-0}"

for svc in services/${COMP}-*; do
  if [ -d "$svc" ]; then
    echo "Building $(basename $svc)"
    docker build -t "${DOCKER_REGISTRY}/atom-cloud/$(basename $svc):${IMAGE_TAG}" "$svc" || echo "build failed (sim)"
  fi
done

if [ "${SIMULATION_MODE}" != "true" ]; then
  terraform -chdir=infra/terraform/modules/${COMP} apply -auto-approve
  helm upgrade --install "${COMP}" infra/helm/${COMP} -n ${NAMESPACE} --wait
  vault policy write "${COMP}" infra/vault/policies/${COMP}.hcl || true
else
  echo "SIMULATION_MODE=true — infra actions skipped."
fi