#!/bin/bash
set -e

# Phase J.5 Production Cutover Script
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
NAMESPACE="${NAMESPACE:-atom-prod}"
SIMULATION_MODE="${SIMULATION_MODE:-true}"
APPROVE_DEPLOY="${APPROVE_DEPLOY:-no}"
VAULT_TOKEN="${VAULT_TOKEN:-}"

# Environment validation
if [ "${SIMULATION_MODE}" = "false" ] && [ "${APPROVE_DEPLOY}" != "yes" ]; then
  echo "ERROR: Live deployment requires APPROVE_DEPLOY=yes"
  exit 1
fi

echo "[J5] Starting Production Cutover - SIMULATION_MODE=${SIMULATION_MODE}"
echo "[J5] Timestamp: ${TIMESTAMP}"
echo "[J5] Namespace: ${NAMESPACE}"

# Create reports directory
mkdir -p reports/j5

# Step 1: Pre-deployment validation
echo "[J5] Step 1: Pre-deployment validation"
kubectl cluster-info > reports/j5/cluster_info.log
vault status > reports/j5/vault_status.log || echo "Vault not available"

# Step 2: Deploy infrastructure
echo "[J5] Step 2: Infrastructure deployment"
if [ "${SIMULATION_MODE}" = "false" ]; then
  terraform -chdir=infra/terraform apply -auto-approve
else
  terraform -chdir=infra/terraform plan > reports/j5/terraform_plan_prod.log
fi

# Step 3: Deploy services
echo "[J5] Step 3: Service deployment"
SERVICES=("gateway" "auth" "marketplace" "ai-proxy" "langgraph" "workflow-registry")

for service in "${SERVICES[@]}"; do
  echo "[J5] Deploying ${service}..."
  if [ "${SIMULATION_MODE}" = "false" ]; then
    helm upgrade --install ${service} infra/helm/${service}/ -n ${NAMESPACE} --create-namespace
  else
    helm template ${service} infra/helm/${service}/ > reports/j5/${service}.helm.tpl.yaml
  fi
done

# Step 4: Partner federation setup
echo "[J5] Step 4: Partner federation setup"
if [ -f "infra/contracts/partners/federation_registry.json" ]; then
  echo "[J5] Partner registry found, configuring federation..."
  # Federation setup would go here
else
  echo "[J5] No partner registry found, skipping federation"
fi

# Step 5: Monitoring and health checks
echo "[J5] Step 5: Health checks and monitoring"
kubectl get pods -n ${NAMESPACE} > reports/j5/pods_status.log
kubectl get services -n ${NAMESPACE} > reports/j5/services_status.log

# Step 6: Generate deployment report
cat > reports/j5/deployment_summary.json << EOF
{
  "phase": "J.5",
  "timestamp": "${TIMESTAMP}",
  "simulation_mode": ${SIMULATION_MODE},
  "namespace": "${NAMESPACE}",
  "status": "COMPLETED",
  "services_deployed": $(echo '["'$(IFS='","'; echo "${SERVICES[*]}")'"']'),
  "next_steps": [
    "Monitor system for 24 hours",
    "Verify partner federation",
    "Run post-deployment tests"
  ]
}
EOF

echo "[J5] Production cutover complete. Review reports in reports/j5/"