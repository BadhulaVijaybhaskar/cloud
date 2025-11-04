#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
COMP="marketplace"

# ensure no phase directories
if ls -d phase-* 2>/dev/null; then
  echo "ERROR: phase-* directories found. Abort." >&2
  exit 2
fi

# check storage access (simulation safe)
echo "Checking artifact bucket access (sim mode)"
if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "SIMULATION_MODE=true - skipping real bucket checks"
else
  # run actual checks
  aws s3 ls "s3://${MODEL_ARTIFACT_BUCKET}" || echo "Bucket check failed"
fi

# db migration check (non-blocking)
if [ -d "services/model-registry/migrations" ]; then
  echo "Migrations present"
fi

echo "PRECHECK_COMPLETE"