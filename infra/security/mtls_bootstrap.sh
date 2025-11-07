#!/usr/bin/env bash
set -euo pipefail

ROOT_CN="${MTLS_ROOT_CN:-atom-l3-root}"
OUT_DIR="${PWD}/infra/security/certs"
mkdir -p "$OUT_DIR"

echo "Generating root key (simulation)..."
echo "SIMULATION_ROOT_KEY" > "$OUT_DIR/root.key"
echo "SIMULATION_ROOT_CERT" > "$OUT_DIR/root.crt"

for name in orchestrator gateway metadata bus auditor; do
  echo "Generating cert for $name (simulation)..."
  echo "SIMULATION_${name}_KEY" > "$OUT_DIR/${name}.key"
  echo "SIMULATION_${name}_CERT" > "$OUT_DIR/${name}.crt"
done

echo "mTLS certificates written to $OUT_DIR (simulation mode)"