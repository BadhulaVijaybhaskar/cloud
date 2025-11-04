#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
COMP="marketplace"

# build docker images (simulation safe)
for svc in services/${COMP}-* services/model-registry services/agent-registry; do
  if [ -d "$svc" ]; then
    echo "Building $(basename $svc)"
    docker build -t "localhost:5000/atom-cloud/$(basename $svc):${IMAGE_TAG:-latest}" "$svc" || echo "build (sim) failed"
  fi
done

if [ "${SIMULATION_MODE}" != "true" ]; then
  terraform -chdir=infra/terraform/modules/${COMP} apply -auto-approve
  helm upgrade --install ${COMP} infra/helm/${COMP} -n ${NAMESPACE} --wait
else
  echo "SIMULATION_MODE=true - skipping infra apply"
fi