#!/usr/bin/env bash
set -euo pipefail

SIMULATION_MODE="${SIMULATION_MODE:-true}"
VAULT_ADDR="${VAULT_ADDR:-https://vault.atom.internal}"
TEST_ROLE="${TEST_ROLE:-l3-test-role}"
TEST_POLICY="${TEST_POLICY:-l3_readonly}"
TEST_COMMON_NAME="${TEST_COMMON_NAME:-test.l3.local}"
TTL="${TTL:-5m}"

echo "Vault PKI & Policy test starting. SIMULATION_MODE=${SIMULATION_MODE}"
echo "VAULT_ADDR=${VAULT_ADDR}"
echo "Role=${TEST_ROLE} Policy=${TEST_POLICY} CN=${TEST_COMMON_NAME} TTL=${TTL}"

if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "[SIMULATION] Would perform:"
  echo "1) vault token create -policy=${TEST_POLICY} -orphan -ttl=${TTL}"
  echo "2) vault write pki/issue/${TEST_ROLE} common_name=${TEST_COMMON_NAME} ttl=${TTL}"
  echo "3) test access to secret: vault kv get secret/l3/test (simulated)"
  exit 0
fi

# Check vault reachable
if ! curl -sSf "${VAULT_ADDR}/v1/sys/health" >/dev/null 2>&1; then
  echo "ERROR: Vault not reachable at ${VAULT_ADDR}"
  exit 1
fi
echo "Vault reachable."

# Create token with the test policy
echo "Creating test token..."
tok_json=$(vault token create -policy="${TEST_POLICY}" -orphan -ttl="${TTL}" -format=json)
TEST_TOKEN=$(echo "${tok_json}" | jq -r '.auth.client_token')
echo "Test token created (short-lived)."

# Issue test certificate from PKI role
echo "Issuing test certificate..."
cert_json=$(VAULT_TOKEN="${TEST_TOKEN}" vault write -format=json pki/issue/"${TEST_ROLE}" common_name="${TEST_COMMON_NAME}" ttl="${TTL}")
echo "Certificate issued."

# Validate test policy access
echo "Validating secret access with test token..."
if VAULT_TOKEN="${TEST_TOKEN}" vault kv get secret/l3/test >/dev/null 2>&1; then
  echo "Secret read succeeded with test token (policy binding OK)."
else
  echo "Warning: Secret read with test token failed. Confirm policies and secret path existence."
fi

echo "Vault PKI & Policy test complete. Revoke test token..."
vault token revoke "${TEST_TOKEN}" || true
echo "Done."