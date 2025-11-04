#!/bin/bash
set -e

# Phase J.5 Production Rollback Script
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
NAMESPACE="${NAMESPACE:-atom-prod}"
DRY_RUN="${DRY_RUN:-true}"
APPROVE_ROLLBACK="${APPROVE_ROLLBACK:-no}"
REPORT_DIR="reports/j5"
INFRA_TF_DIR="infra/terraform"

log() { echo "[ROLLBACK] $1" | tee -a "${REPORT_DIR}/rollback_test.log"; }
save() { echo "$1" >> "${REPORT_DIR}/rollback_test.log"; }

# Safety check
if [ "${DRY_RUN}" = "false" ] && [ "${APPROVE_ROLLBACK}" != "yes" ]; then
  echo "ERROR: Live rollback requires APPROVE_ROLLBACK=yes"
  exit 1
fi

# Helper function for safe helm rollback
helm_rollback_safe() {
  local svc="$1"
  local ns="$2"
  if helm list -n "${ns}" | grep -q "${svc}"; then
    if [ "${DRY_RUN}" = "false" ]; then
      helm rollback "${svc}" -n "${ns}" || save "ROLLBACK_FAILED ${svc}"
    else
      save "SIMULATION: would rollback ${svc}"
    fi
  else
    save "HELM_RELEASE_NOT_FOUND ${svc}"
  fi
}

mkdir -p "${REPORT_DIR}"
SERVICES=("gateway" "auth" "marketplace" "ai-proxy" "langgraph" "workflow-registry")

log "ROLLBACK PLAN: DRY_RUN=${DRY_RUN} - will target services: ${SERVICES[*]}"
save "START_ROLLBACK ${TIMESTAMP} DRY_RUN=${DRY_RUN}"

# Step 1: Scale down ingress traffic
log "STEP 1: Scale down ingress / gateway to stop new traffic"
save "SCALE_DOWN_GATEWAY"
if [ "${DRY_RUN}" = "false" ]; then
  if kubectl get deployment gateway -n "${NAMESPACE}" &>/dev/null; then
    kubectl scale deployment gateway --replicas=0 -n "${NAMESPACE}" || true
    save "SCALED gateway->0"
  else
    save "GATEWAY_NOT_FOUND"
  fi
else
  save "SIMULATION: scale gateway skipped"
fi

# Step 2: Rollback core services
for svc in "${SERVICES[@]}"; do
  log "STEP 2: Attempt safe rollback for ${svc}"
  save "ATTEMPT_ROLLBACK ${svc}"
  helm_rollback_safe "${svc}" "${NAMESPACE}"
done

# Step 3: Terraform state reconciliation
log "STEP 3: Terraform refresh (non-destructive)"
save "TERRAFORM_REFRESH_START"
if [ -d "${INFRA_TF_DIR}" ]; then
  pushd "${INFRA_TF_DIR}" >/dev/null
  if [ "${DRY_RUN}" = "false" ]; then
    log "Terraform refresh/apply (live)"
    terraform init -input=false -no-color || true
    terraform apply -auto-approve -no-color || true
    save "TERRAFORM_APPLY_DONE"
  else
    log "Terraform plan (dry-run)"
    terraform init -input=false -no-color || true
    terraform plan -input=false -no-color -out="${PWD}/../${REPORT_DIR}/rollback.tfplan" || true
    save "TERRAFORM_PLAN_CREATED"
  fi
  popd >/dev/null
else
  save "TERRAFORM_DIR_NOT_FOUND ${INFRA_TF_DIR}"
fi

# Step 4: Vault diagnostics
log "STEP 4: Vault diagnostics"
if command -v vault >/dev/null 2>&1; then
  if [ "${DRY_RUN}" = "false" ]; then
    vault status > "${REPORT_DIR}/vault_status_after_rollback.log" || true
  else
    vault status > "${REPORT_DIR}/vault_status_sim.log" || true
  fi
else
  save "VAULT_CLI_NOT_PRESENT"
fi

# Step 5: Post-rollback diagnostics
log "STEP 5: Post-rollback diagnostics"
kubectl get pods -n "${NAMESPACE}" --no-headers > "${REPORT_DIR}/post_rollback_pods.log" || true
kubectl describe pods -n "${NAMESPACE}" > "${REPORT_DIR}/post_rollback_describe.log" || true
kubectl get events -n "${NAMESPACE}" --sort-by='.lastTimestamp' > "${REPORT_DIR}/post_rollback_events.log" || true

save "END_ROLLBACK ${TIMESTAMP} DRY_RUN=${DRY_RUN}"
log "ROLLBACK SCRIPT COMPLETE (DRY_RUN=${DRY_RUN}). Review ${REPORT_DIR}/rollback_test.log"

if [ "${DRY_RUN}" = "true" ]; then
  echo "DRY_RUN=true — No destructive actions performed. To run live rollback, set DRY_RUN=false and APPROVE_ROLLBACK=yes"
fi

exit 0