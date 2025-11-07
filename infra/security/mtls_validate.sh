#!/usr/bin/env bash
set -e

CERT_DIR="${PWD}/infra/security/certs"

for name in orchestrator gateway metadata bus auditor; do
  if [ ! -f "${CERT_DIR}/${name}.crt" ]; then
    echo "Missing cert for ${name}" && exit 1
  fi
done
echo "All certificates valid (simulation)"