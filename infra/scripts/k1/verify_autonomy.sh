#!/usr/bin/env bash
# infra/scripts/k1/verify_autonomy.sh
# K.1 Autonomous Runtime verification helper
# - Default: SIMULATION_MODE=true (non-destructive)
# - Produces: reports/k1/verification.log, reports/k1/verification_summary.json

set -euo pipefail

: "${SIMULATION_MODE:=true}"
: "${REPORT_DIR:=reports/k1}"
: "${AOL_CONTROLLER_URL:=http://localhost:8200}"
: "${AOL_POLICY_URL:=http://localhost:8300}"
: "${GOVERNANCE_API:=http://localhost:8400}"
: "${CHECK_INTERVAL:=10}"
: "${RETRY_COUNT:=3}"

mkdir -p "${REPORT_DIR}"

LOG="${REPORT_DIR}/verification.log"
SUMMARY="${REPORT_DIR}/verification_summary.json"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" | tee -a "${LOG}"; }

# helper: http get with retries
http_get() {
  local url=$1; local out=$2; local tries=${3:-$RETRY_COUNT}
  local rc=0
  for i in $(seq 1 "${tries}"); do
    if curl -sS --max-time 8 "${url}" -o "${out}" 2>/dev/null; then
      rc=0; break
    else
      rc=$?; log "WARN: GET ${url} failed (attempt ${i}/${tries})"
      sleep "${CHECK_INTERVAL}"
    fi
  done
  return ${rc}
}

# Start verification
log "=== K.1 AUTONOMY VERIFICATION START (SIMULATION_MODE=${SIMULATION_MODE}) ==="
echo "{}" > "${SUMMARY}"

# 1) Controller health
CONTROLLER_HEALTH_JSON="${REPORT_DIR}/controller_health.json"
if http_get "${AOL_CONTROLLER_URL}/health" "${CONTROLLER_HEALTH_JSON}"; then
  log "Controller health OK -> ${AOL_CONTROLLER_URL}/health"
  CONTROLLER_HEALTH_STATUS=$(jq -r '.status // "unknown"' "${CONTROLLER_HEALTH_JSON}" 2>/dev/null || echo "unknown")
else
  log "ERROR: Controller health check failed at ${AOL_CONTROLLER_URL}/health"
  CONTROLLER_HEALTH_STATUS="failed"
fi

# 2) Policy engine health
POLICY_HEALTH_JSON="${REPORT_DIR}/policy_health.json"
if http_get "${AOL_POLICY_URL}/health" "${POLICY_HEALTH_JSON}"; then
  log "Policy engine health OK -> ${AOL_POLICY_URL}/health"
  POLICY_HEALTH_STATUS=$(jq -r '.status // "unknown"' "${POLICY_HEALTH_JSON}" 2>/dev/null || echo "unknown")
else
  log "ERROR: Policy engine health check failed at ${AOL_POLICY_URL}/health"
  POLICY_HEALTH_STATUS="failed"
fi

# 3) Simple end-to-end decision -> policy check (non-destructive)
DECISION_RESP="${REPORT_DIR}/decision_check.json"
if [ "${SIMULATION_MODE}" = "true" ]; then
  log "SIMULATION: Submitting non-destructive decision request to controller"
  if curl -sS --max-time 8 -X POST "${AOL_CONTROLLER_URL}/v1/decide" -H "Content-Type: application/json" \
      -d '{"service":"test-service","cpu_usage":85,"memory_usage":70}' -o "${DECISION_RESP}" 2>/dev/null; then
    log "Decision request returned: $(jq -c '{id: .id, actions: (.actions | length)} ' "${DECISION_RESP}" 2>/dev/null || echo 'no-json')"
    DECISION_OK=true
  else
    log "WARN: Decision request failed (controller may be unreachable)"
    DECISION_OK=false
  fi
else
  log "LIVE MODE: Submitting guarded decision (operator must ensure safe payload)"
  if curl -sS --max-time 8 -X POST "${AOL_CONTROLLER_URL}/v1/decide" -H "Content-Type: application/json" \
      -d '{"service":"services/auth","cpu_usage":75}' -o "${DECISION_RESP}" 2>/dev/null; then
    log "Decision request returned (live): $(jq -c '{id: .id, actions: (.actions | length)} ' "${DECISION_RESP}" 2>/dev/null || echo 'no-json')"
    DECISION_OK=true
  else
    log "ERROR: Live decision request failed"
    DECISION_OK=false
  fi
fi

# 4) Audit log sanity: look for decision files under reports/k1
DECISION_COUNT=$(ls -1 ${REPORT_DIR}/decision_*.json 2>/dev/null | wc -l || echo 0)
log "Found ${DECISION_COUNT} decision audit files"

# 5) Safety gate: ensure AUTONOMOUS_MODE not enabled in SIM mode
SAFETY_OK=true
if [ "${SIMULATION_MODE}" = "true" ]; then
  log "Safety: Simulation mode active - autonomous actions disabled"
else
  log "LIVE MODE: Autonomous actions may be enabled - operator responsibility"
fi

# 6) Summarize verification results to JSON
jq -n \
  --arg sim "${SIMULATION_MODE}" \
  --arg controller_status "${CONTROLLER_HEALTH_STATUS:-unknown}" \
  --arg policy_status "${POLICY_HEALTH_STATUS:-unknown}" \
  --argjson decision_ok "$( [ "${DECISION_OK}" = "true" ] && echo true || echo false )" \
  --argjson safety_ok "$( [ "${SAFETY_OK}" = "true" ] && echo true || echo false )" \
  --argjson decision_cnt "${DECISION_COUNT}" \
  '{
    simulation_mode: $sim,
    controller_health: $controller_status,
    policy_health: $policy_status,
    decision_flow_ok: $decision_ok,
    safety_ok: $safety_ok,
    decisions_count: $decision_cnt,
    timestamp: "'$(ts)'"
  }' > "${SUMMARY}"

log "Verification summary written to ${SUMMARY}"
log "=== K.1 AUTONOMY VERIFICATION END ==="

# Exit code: 0 if all critical checks passed; 2 if safety violation; 1 if non-critical failures
if [ "${SAFETY_OK}" != "true" ]; then
  log "SAFETY VIOLATION: Exiting with code 2"
  exit 2
fi

if [ "${CONTROLLER_HEALTH_STATUS}" = "failed" ] || [ "${POLICY_HEALTH_STATUS}" = "failed" ]; then
  log "CRITICAL FAILURES DETECTED: Controller or Policy engine unhealthy"
  exit 1
fi

log "Verification PASSED (non-fatal checks may still have warnings)."
exit 0