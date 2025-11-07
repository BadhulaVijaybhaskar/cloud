#!/usr/bin/env bash
set -euo pipefail

SIMULATION_MODE=${SIMULATION_MODE:-true}
VAULT_ADDR=${VAULT_ADDR:-"https://vault.atom.internal"}
POLICIES_DIR="infra/vault/policies"
LOG="reports/l3/vault_apply.log"

mkdir -p reports/l3

echo "Starting Vault policy apply. SIMULATION_MODE=${SIMULATION_MODE}" | tee "$LOG"

for f in "${POLICIES_DIR}"/*.hcl; do
  [ -f "$f" ] || continue
  policy_name=$(basename "$f" .hcl)
  echo "Processing policy: $policy_name (file: $f)" | tee -a "$LOG"

  if [ "$SIMULATION_MODE" = "true" ]; then
    echo "SIMULATION_MODE: would run -> vault policy write ${policy_name} ${f}" | tee -a "$LOG"
  else
    echo "Applying policy ${policy_name} to Vault at ${VAULT_ADDR}..." | tee -a "$LOG"
    vault policy write "${policy_name}" "${f}" 2>&1 | tee -a "$LOG"
    echo "Verifying readback..." | tee -a "$LOG"
    vault policy read "${policy_name}" > /dev/null
    echo "Policy ${policy_name} applied." | tee -a "$LOG"
  fi
done

echo "Completed Vault policy apply (simulation=${SIMULATION_MODE})" | tee -a "$LOG"