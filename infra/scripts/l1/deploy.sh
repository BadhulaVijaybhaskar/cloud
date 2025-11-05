#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/l1"
mkdir -p "${REPORTS}"

echo "L.1 deploy - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Simulated terraform plan/helm template
cat > "${REPORTS}/deploy_summary.json" <<JSON
{
  "phase":"L.1",
  "timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "simulation_mode":true,
  "steps":[
    {"step":"terraform_plan","result":"simulated"},
    {"step":"helm_template","result":"simulated"},
    {"step":"register_sample_nodes","result":"simulated"}
  ],
  "overall_status":"SIM_OK"
}
JSON

# Create federation health stub
cat > "${REPORTS}/federation_health.json" <<JSON
{
  "nodes_registered": 0,
  "nodes_opted_in": [],
  "last_sync":"none",
  "note":"Simulation - no live nodes registered"
}
JSON

echo "Deploy (simulation) wrote deploy_summary.json and federation_health.json"