#!/bin/bash
set -euo pipefail
SIM="${SIMULATION_MODE:-true}"
REPORTS="${REPORTS_PATH:-reports/k9}"
mkdir -p "$REPORTS"
TMP="${REPORTS}/deploy_summary.json.tmp"
echo "{}" > "$TMP"

if [ "$SIM" = "true" ]; then
  python - <<PY
import json
out={'phase':'K.9','simulation_mode':True,'steps':[]}
out['steps'].append({'step':'terraform_plan','result':'simulated','module':'infra/terraform/modules/k9_ai_marketing'})
out['steps'].append({'step':'helm_template','result':'simulated','chart':'infra/helm/k9-ai-marketing'})
out['steps'].append({'step':'service_start','result':'simulated','services':['k9-agent-core','k9-simulator','k9-trainer','k9-api','k9-experiment-store']})
out['overall_status']='SIM_OK'
print(json.dumps(out,indent=2))
PY
else
  if [ "${APPROVE_K9_DEPLOY:-no}" != "yes" ]; then
    echo '{"error":"APPROVE_K9_DEPLOY not yes"}' > "$TMP"
    echo "Live deploy aborted - APPROVE_K9_DEPLOY not set"
    exit 1
  fi
  # Live deploy placeholder (operator responsibility)
  echo '{"phase":"K.9","simulation_mode":false,"overall_status":"LIVE_STARTED"}' > "$TMP"
fi

mv "$TMP" "${REPORTS}/deploy_summary.json"
echo "Deploy summary -> ${REPORTS}/deploy_summary.json"