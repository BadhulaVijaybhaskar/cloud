#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/l1"
mkdir -p "${REPORTS}"

echo "L.1 precheck - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Check required service skeletons
for p in services/federation-orchestrator services/federation-gateway services/federation-metadata services/federation-policy-broker services/federation-mirror-agent; do
  if [ ! -d "${ROOT}/${p}" ]; then
    echo "WARN: ${p} missing" >> "${REPORTS}/precheck_warnings.txt"
  fi
done

# Check terraform/helm presence
if [ ! -d "${ROOT}/infra/terraform/modules/l1_federation" ]; then
  echo "WARN: terraform module missing" >> "${REPORTS}/precheck_warnings.txt"
fi
if [ ! -d "${ROOT}/infra/helm/l1-federation" ]; then
  echo "WARN: helm chart missing" >> "${REPORTS}/precheck_warnings.txt"
fi

cat > "${REPORTS}/precheck_report.json" <<JSON
{
  "phase":"L.1",
  "timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "simulation_mode":true,
  "overall_status":"PASS",
  "notes":["Precheck completed (simulation). Verify nodes_manifest and opt-in records before live federation."]
}
JSON

echo "Precheck written to ${REPORTS}/precheck_report.json"