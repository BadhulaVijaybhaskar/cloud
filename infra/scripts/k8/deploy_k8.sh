#!/usr/bin/env bash
set -euo pipefail
SIM=${SIMULATION_MODE:-true}
mkdir -p reports/k8
LOG=reports/k8/deploy.log
echo "K.8 deploy - SIMULATION_MODE=${SIM}" | tee ${LOG}

if [ "${SIM}" = "true" ]; then
  # Simulate terraform plan/helm render
  cat > reports/k8/terraform_plan_k8.json <<'JSON'
{"plan":{"to_create":5,"to_change":0,"to_destroy":0}}
JSON
  echo '{"helm_template":"rendered (simulated)"}' > reports/k8/helm_template_k8.yaml
  echo '{"deploy":"SIM_OK","notes":"No live infra changed"}' > reports/k8/deploy_summary.json
  echo "Deploy simulation completed" | tee -a ${LOG}
  exit 0
fi

# Live deploy (operator-only)
terraform -chdir=infra/terraform/modules/k8_billing init
terraform -chdir=infra/terraform/modules/k8_billing plan -out=reports/k8/terraform_plan_k8.tfplan
terraform -chdir=infra/terraform/modules/k8_billing apply -auto-approve reports/k8/terraform_plan_k8.tfplan
helm upgrade --install k8-billing infra/helm/k8-billing --namespace atom-k8 --create-namespace
if [ -f infra/vault/policies/k8_billing.hcl ]; then
  vault policy write k8_billing infra/vault/policies/k8_billing.hcl
fi
echo '{"deploy":"LIVE_OK"}' > reports/k8/deploy_summary.json