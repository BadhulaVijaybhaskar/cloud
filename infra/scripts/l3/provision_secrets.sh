#!/usr/bin/env bash
set -euo pipefail

SIMULATION_MODE=${SIMULATION_MODE:-true}
VAULT_ADDR=${VAULT_ADDR:-"https://vault.atom.internal"}
LOG="reports/l3/vault_provision.log"

mkdir -p reports/l3
echo "Provisioning secrets (SIMULATION_MODE=${SIMULATION_MODE})" | tee "$LOG"

declare -A SECRETS
SECRETS["l3-orchestrator"]="secret/data/l3/orchestrator"
SECRETS["l3-gateway"]="secret/data/l3/gateway"
SECRETS["l3-metadata"]="secret/data/l3/metadata"
SECRETS["l3-bus"]="secret/data/l3/bus"
SECRETS["l3-auditor"]="secret/data/l3/auditor"

for svc in "${!SECRETS[@]}"; do
  path=${SECRETS[$svc]}
  echo "=> ${svc} -> ${path}" | tee -a "$LOG"
  if [ "$SIMULATION_MODE" = "true" ]; then
    echo "SIMULATION: vault kv put ${path} api_key=SIM_PLACEHOLDER" | tee -a "$LOG"
  else
    vault kv put "${path}" api_key="$(openssl rand -hex 32)" 2>&1 | tee -a "$LOG"
    echo "Wrote secret for ${svc}" | tee -a "$LOG"
  fi
done

echo "Secret provisioning complete." | tee -a "$LOG"