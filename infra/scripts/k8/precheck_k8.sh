#!/usr/bin/env bash
set -euo pipefail
SIM=${SIMULATION_MODE:-true}
mkdir -p reports/k8
LOG=reports/k8/precheck.log
echo "K.8 precheck - SIMULATION_MODE=${SIM}" | tee ${LOG}

# Check expected infra folders
OK=true
[ -d infra/terraform/modules/k8_billing ] || { echo "MISSING: infra/terraform/modules/k8_billing" | tee -a ${LOG}; OK=false; }
[ -d infra/helm/k8-billing ] || { echo "MISSING: infra/helm/k8-billing" | tee -a ${LOG}; OK=false; }
[ -f infra/contracts/billing_event.yaml ] || { echo "MISSING: infra/contracts/billing_event.yaml" | tee -a ${LOG}; OK=false; }
[ -d services ] || { echo "MISSING: services/ folder" | tee -a ${LOG}; OK=false; }

if [ "${OK}" != "true" ]; then
  echo '{"phase":"K.8","status":"FAIL_PRECHECK","notes":"Missing required files/folders. See precheck.log"}' > reports/k8/precheck_report.json
  exit 2
fi

if [ "${SIM}" = "true" ]; then
  cat > reports/k8/precheck_report.json <<'JSON'
{
  "phase":"K.8",
  "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "simulation_mode": true,
  "overall_status":"PASS_SIMULATION",
  "notes":["All required stubs present","Simulation mode: no live actions performed"]
}
JSON
  echo "Precheck (simulation) passed" | tee -a ${LOG}
  exit 0
fi

# Live-mode checks (operator must run)
echo "Performing live prechecks..."
vault status >/dev/null 2>&1 || { echo "Vault unreachable" | tee -a ${LOG}; echo '{"phase":"K.8","status":"FAIL_VAULT"}' > reports/k8/precheck_report.json; exit 3; }
# Add other live checks as needed...
echo '{"phase":"K.8","status":"PASS","notes":["Live precheck passed"]}' > reports/k8/precheck_report.json