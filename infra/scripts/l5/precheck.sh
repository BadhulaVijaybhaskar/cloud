#!/bin/bash
set -e

echo "Running L.5 precheck..."
mkdir -p reports/l5

# Check model artifacts
if [ -f "models/l5/base_distilled.pkl" ]; then
  model_ok=true
else
  model_ok=false
fi

jq -n --arg model "$model_ok" --arg sim "${SIMULATION_MODE}" \
  '{phase:"L.5",timestamp:(now|todate),simulation_mode:$sim, model_present:$model}' > reports/l5/precheck_report.json

if [ "${SIMULATION_MODE}" != "true" ] && [ "$model_ok" = "false" ]; then
  echo "ERROR: base_distilled model missing in live mode"
  exit 1
fi

echo "Precheck complete."