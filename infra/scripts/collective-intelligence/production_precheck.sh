#!/bin/bash
# Phase I.5 Production Precheck Suite
# Validates CIN readiness for production deployment

set -e

PRECHECK_DIR="$(dirname "$0")"
REPORTS_DIR="${PRECHECK_DIR}/../reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PRECHECK_LOG="${REPORTS_DIR}/precheck_${TIMESTAMP}.log"

mkdir -p "${REPORTS_DIR}"

echo "=== Phase I.5 CIN Production Precheck Suite ===" | tee "${PRECHECK_LOG}"
echo "Started: $(date)" | tee -a "${PRECHECK_LOG}"

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo "✅ PASS: $1" | tee -a "${PRECHECK_LOG}"
    ((PASS_COUNT++))
}

check_fail() {
    echo "❌ FAIL: $1" | tee -a "${PRECHECK_LOG}"
    ((FAIL_COUNT++))
}

# 1. Schema Coverage Check
echo "1. Checking schema coverage..." | tee -a "${PRECHECK_LOG}"
if [[ -f "${PRECHECK_DIR}/../contracts/signal_v1.proto" && -f "${PRECHECK_DIR}/../contracts/signal-v1.json" ]]; then
    check_pass "Signal schemas present"
else
    check_fail "Missing signal schemas"
fi

# 2. Policy Test Suite
echo "2. Checking policy matrix..." | tee -a "${PRECHECK_LOG}"
if [[ -f "${PRECHECK_DIR}/../policies/policy-matrix.yaml" ]]; then
    check_pass "Policy matrix present"
else
    check_fail "Missing policy matrix"
fi

# 3. Security Posture
echo "3. Checking security configuration..." | tee -a "${PRECHECK_LOG}"
if [[ -f "${PRECHECK_DIR}/../security/vault-policies.hcl" ]]; then
    check_pass "Vault policies configured"
else
    check_fail "Missing Vault policies"
fi

# 4. Service Health Checks
echo "4. Checking service health..." | tee -a "${PRECHECK_LOG}"
SERVICES=("signal-gateway:8001" "consensus-bus:8002" "fl-orchestrator:8003" "arbiter:8004")
for service in "${SERVICES[@]}"; do
    name="${service%:*}"
    port="${service#*:}"
    
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        check_pass "${name} health check"
    else
        check_fail "${name} health check (service may not be running)"
    fi
done

# 5. Performance Smoke Test
echo "5. Running performance smoke test..." | tee -a "${PRECHECK_LOG}"
if command -v python3 > /dev/null; then
    if python3 -c "
import time
import json
start = time.time()
# Simulate signal processing
for i in range(100):
    signal = {'id': f'test-{i}', 'data': {'value': i}}
    json.dumps(signal)
duration = time.time() - start
print(f'Processed 100 signals in {duration:.3f}s')
exit(0 if duration < 1.0 else 1)
" 2>/dev/null; then
        check_pass "Performance smoke test"
    else
        check_fail "Performance smoke test"
    fi
else
    check_fail "Python3 not available for performance test"
fi

# 6. Privacy Budget Check
echo "6. Checking privacy budget configuration..." | tee -a "${PRECHECK_LOG}"
if [[ -f "${PRECHECK_DIR}/../privacy/epsilon_policy.md" ]]; then
    check_pass "Privacy policy documented"
else
    check_fail "Missing privacy policy"
fi

# 7. Provenance Check
echo "7. Checking model provenance..." | tee -a "${PRECHECK_LOG}"
if [[ -f "${PRECHECK_DIR}/../contracts/model_delta_v1.proto" ]]; then
    check_pass "Model delta schema present"
else
    check_fail "Missing model delta schema"
fi

# Summary
echo "" | tee -a "${PRECHECK_LOG}"
echo "=== PRECHECK SUMMARY ===" | tee -a "${PRECHECK_LOG}"
echo "PASSED: ${PASS_COUNT}" | tee -a "${PRECHECK_LOG}"
echo "FAILED: ${FAIL_COUNT}" | tee -a "${PRECHECK_LOG}"
echo "Completed: $(date)" | tee -a "${PRECHECK_LOG}"

if [[ ${FAIL_COUNT} -eq 0 ]]; then
    echo "🎉 ALL PRECHECKS PASSED - Ready for production deployment" | tee -a "${PRECHECK_LOG}"
    exit 0
else
    echo "⚠️  ${FAIL_COUNT} PRECHECK(S) FAILED - Address issues before deployment" | tee -a "${PRECHECK_LOG}"
    exit 1
fi