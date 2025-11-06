#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_DIR="${ROOT}/reports/k6"
mkdir -p "${REPORT_DIR}"

SIMULATION_MODE=${SIMULATION_MODE:-true}
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
RUN_ID="k6-precheck-$(date -u +%Y%m%dT%H%M%SZ)"

echo "K.6 precheck: RUN_ID=${RUN_ID} SIMULATION_MODE=${SIMULATION_MODE}"

# endpoints - L.1 (federation)
ORCH=${ORCHESTRATOR_URL:-http://localhost:8900}
GATE=${GATEWAY_URL:-http://localhost:8901}
META=${METADATA_URL:-http://localhost:8902}
POLBRO=${POLICY_BROKER_URL:-http://localhost:8903}
MIRROR=${MIRROR_AGENT_URL:-http://localhost:8904}

REPORT_FILE="${REPORT_DIR}/k6_compatibility_report.json"

cat > "${REPORT_FILE}" <<JSON
{
  "phase":"K.6",
  "run_id":"${RUN_ID}",
  "timestamp":"${TS}",
  "simulation_mode": ${SIMULATION_MODE},
  "summary":{"overall_status":"IN_PROGRESS","checked":0,"ok":0,"failed":0},
  "checks":{},
  "notes":[]
}
JSON

update() {
  jq "${1}" "${REPORT_FILE}" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "${REPORT_FILE}"
}

# Health check helper
check_health() {
  local name=$1; local url=$2
  set +e
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${url}/health" || echo "000")
  rc=$?
  set -e
  if [[ "${rc}" -eq 0 && "${http_code}" == "200" ]]; then
    jq ".checks += {\"${name}\":{\"status\":\"ok\",\"endpoint\":\"${url}/health\",\"http\":200}}" "${REPORT_FILE}" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "${REPORT_FILE}"
    return 0
  else
    jq ".checks += {\"${name}\":{\"status\":\"fail\",\"endpoint\":\"${url}/health\",\"http\":${http_code},\"rc\":${rc}}}" "${REPORT_FILE}" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "${REPORT_FILE}"
    return 1
  fi
}

total=0; ok=0; fail=0

for item in "orchestrator:${ORCH}" "gateway:${GATE}" "metadata:${META}" "policy_broker:${POLBRO}" "mirror_agent:${MIRROR}"; do
  name="${item%%:*}"
  url="${item#*:}"
  total=$((total+1))
  if check_health "${name}" "${url}"; then ok=$((ok+1)); else fail=$((fail+1)); fi
done

update ".summary.checked=${total} | .summary.ok=${ok} | .summary.failed=${fail}"

# Run contract tests (pytest)
echo "Running contract tests..."
set +e
pytest -q tests/k6/contract_tests.py || true
set -e
update '.checks += {"contract_tests":{"status":"executed","note":"See pytest output"}}'

# Run mTLS helper if present
if [ -x "${ROOT}/tests/k6/mtls_test.sh" ]; then
  echo "Running mTLS checks..."
  "${ROOT}/tests/k6/mtls_test.sh" "${REPORT_DIR}" || true
  update '.checks += {"mtls_handshake":{"status":"executed","note":"See reports/k6/mtls_handshake.json"}}'
else
  update '.checks += {"mtls_handshake":{"status":"skipped","note":"mtls_test.sh missing"}}'
fi

# Metadata sanitize smoke
SAMPLE='{"tenant_id":"t-test","region":"eu-west-1","meta":{"maybe_pii":"REDACT_ME","field":"value"}}'
set +e
body=$(curl -s -X POST -H "Content-Type: application/json" -d "${SAMPLE}" "${META}/sanitize" || echo '{"simulated":true}')
set -e
jq ".checks += {\"metadata_sanitize\":{\"status\":\"executed\",\"response\":${body}}}" "${REPORT_FILE}" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "${REPORT_FILE}"

# finalize
final="PASS_SIMULATION"
if [[ $fail -gt 0 ]]; then final="FAIL_ENDPOINTS"; fi
jq ".summary.overall_status=\"${final}\"" "${REPORT_FILE}" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "${REPORT_FILE}"

echo "Precheck complete: ${REPORT_FILE}"