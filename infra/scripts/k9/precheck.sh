#!/bin/bash
set -euo pipefail
SIM="${SIMULATION_MODE:-true}"
REPORTS="${REPORTS_PATH:-reports/k9}"
mkdir -p "$REPORTS"
echo "Running K.9 precheck (SIMULATION_MODE=${SIM})" > "${REPORTS}/precheck_report.json.tmp"

python - <<PY
import json, os
r={'phase':'K.9','simulation_mode':os.getenv('SIMULATION_MODE','true')}
services=['k9-agent-core','k9-simulator','k9-trainer','k9-api','k9-experiment-store']
r['services']={s: os.path.isdir(os.path.join('services',s)) for s in services}
r['models']={'base_model_present': os.path.exists('models/k9/base_marketing_model.pkl')}
r['overall_status']='PASS' if all(r['services'].values()) and r['models']['base_model_present'] else 'WARN'
print(json.dumps(r,indent=2))
PY

mv "${REPORTS}/precheck_report.json.tmp" "${REPORTS}/precheck_report.json"
echo "Precheck report -> ${REPORTS}/precheck_report.json"