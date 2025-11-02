#!/usr/bin/env bash
set -euo pipefail
: "${ATOM_ROOT:=/workspace/atom-cloud}"
: "${SIMULATION_MODE:=true}"
mkdir -p "$ATOM_ROOT/reports/i9"
echo "I9 Preflight - SIMULATION_MODE=${SIMULATION_MODE}" > "$ATOM_ROOT/reports/i9/preflight.txt"
if [ "$SIMULATION_MODE" = "false" ]; then
  echo "Checking Hasura..."
  curl -sSf "${HASURA_URL:-http://localhost:8080}/healthz" || { echo "Hasura unreachable"; exit 2; }
  echo "Hasura OK" >> "$ATOM_ROOT/reports/i9/preflight.txt"
fi
echo "Preflight complete"