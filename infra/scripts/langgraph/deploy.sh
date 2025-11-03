#!/bin/bash
set -e
: "${SIMULATION_MODE:=true}"
COMPONENT_NAME="langgraph"

echo "Running $COMPONENT_NAME deployment in SIMULATION_MODE=$SIMULATION_MODE"

# AGENT INSTRUCTION: Always run in SIMULATION_MODE=true unless all dependent infrastructure modules are live and verified
# Never attempt Terraform apply or Helm install in live mode during simulation

SERVICES_PATH="services"
INFRA_PATH="infra"
SECURITY_PATH="infra/security"
POLICIES_PATH="infra/vault/policies"

echo "Deploying ${COMPONENT_NAME} services..."

# Build services in simulation mode
for service in ${SERVICES_PATH}/langgraph-core ${SERVICES_PATH}/langgraph-api ${SERVICES_PATH}/langgraph-worker; do
    if [ -d "$service" ]; then
        echo "Building $(basename $service) in SIMULATION_MODE=$SIMULATION_MODE..."
        if [ "$SIMULATION_MODE" = "true" ]; then
            echo "SIMULATED: docker build -t ${DOCKER_REGISTRY:-localhost:5000}/atom-cloud/$(basename $service):latest $service"
        else
            docker build -t "${DOCKER_REGISTRY:-localhost:5000}/atom-cloud/$(basename $service):latest" "$service"
        fi
    fi
done

# Apply security policies
if [ -d "${SECURITY_PATH}/${COMPONENT_NAME}" ]; then
    echo "Applying security policies in SIMULATION_MODE=$SIMULATION_MODE..."
    if [ "$SIMULATION_MODE" = "true" ]; then
        echo "SIMULATED: kubectl apply -f ${SECURITY_PATH}/${COMPONENT_NAME}/"
    else
        kubectl apply -f "${SECURITY_PATH}/${COMPONENT_NAME}/" || echo "kubectl apply failed"
    fi
fi

# Deploy infrastructure only in live mode
if [ "$SIMULATION_MODE" != "true" ]; then
    echo "Deploying infrastructure in live mode..."
    terraform -chdir="${INFRA_PATH}/terraform/modules/${COMPONENT_NAME}" apply -auto-approve
    helm upgrade --install "${COMPONENT_NAME}" "${INFRA_PATH}/helm/${COMPONENT_NAME}"
    if [ -f "${POLICIES_PATH}/${COMPONENT_NAME}.hcl" ]; then
        vault policy write "${COMPONENT_NAME}" "${POLICIES_PATH}/${COMPONENT_NAME}.hcl"
    fi
else
    echo "SIMULATION_MODE=true - skipping terraform/helm deployment"
    echo "SIMULATED: terraform apply for ${COMPONENT_NAME}"
    echo "SIMULATED: helm install ${COMPONENT_NAME}"
    echo "SIMULATED: vault policy write ${COMPONENT_NAME}"
fi

echo "Deployment complete for ${COMPONENT_NAME} (SIMULATION_MODE=$SIMULATION_MODE)"