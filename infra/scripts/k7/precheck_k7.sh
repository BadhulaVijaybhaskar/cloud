#!/usr/bin/env bash
set -e
REPORTS="reports/k7"
mkdir -p "${REPORTS}"

echo "Running K.7 precheck (SIMULATION_MODE=${SIMULATION_MODE:-true})"

# quick folder checks
missing=0
for dir in services/partner-portal services/marketplace-v2 services/partner-sandbox services/partner-onboard-worker; do
  if [ ! -d "$dir" ]; then
    echo "MISSING: $dir"
    missing=$((missing+1))
  fi
done

cat > "${REPORTS}/precheck_report.json" <<JSON
{
  "phase":"K.7",
  "simulation_mode":"${SIMULATION_MODE:-true}",
  "services_present":{
    "partner_portal":$( [ -d "services/partner-portal" ] && echo true || echo false ),
    "marketplace_v2":$( [ -d "services/marketplace-v2" ] && echo true || echo false ),
    "partner_sandbox":$( [ -d "services/partner-sandbox" ] && echo true || echo false )
  },
  "overall_status":"$( if [ $missing -eq 0 ]; then echo "PASS"; else echo "FAIL"; fi )"
}
JSON

if [ $missing -ne 0 ]; then
  echo "Precheck FAIL: missing services. See ${REPORTS}/precheck_report.json"
  exit 2
fi

echo "Precheck PASS. Report at ${REPORTS}/precheck_report.json"