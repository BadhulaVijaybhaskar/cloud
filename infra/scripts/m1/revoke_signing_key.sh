#!/bin/bash
set -e

echo "Revoking M.1 GCA signing key (SIMULATION_MODE=${SIMULATION_MODE:-true})"

if [ "${SIMULATION_MODE:-true}" = "true" ]; then
  echo "SIMULATION: Would revoke signing key and update CRL"
  echo "SIMULATION: Would notify all federations of key revocation"
else
  echo "MANUAL_EXECUTION_REQUIRED: Real key revocation needs manual approval"
  echo "Steps:"
  echo "1. vault kv delete secret/m1/gca/signing_key"
  echo "2. Update certificate revocation list"
  echo "3. Notify federation partners"
fi

echo "Key revocation process complete"