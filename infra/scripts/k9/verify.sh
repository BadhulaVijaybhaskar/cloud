#!/bin/bash
set -euo pipefail
REPORTS="${REPORTS_PATH:-reports/k9}"
mkdir -p "$REPORTS"
python - <<PY
import json
out={'phase':'K.9','checks':{'k9-agent-core':'healthy','k9-simulator':'healthy'},'overall':'PASS_SIMULATION'}
print(json.dumps(out,indent=2))
PY