#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/k5"
mkdir -p "${REPORTS}"

echo "K.5 deploy - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Simulated terraform/helm outputs
cat > "${REPORTS}/deploy_summary.json" <<JSON
{
  "phase":"K.5",
  "timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "simulation_mode":true,
  "steps":[
    {"step":"terraform_plan","result":"simulated"},
    {"step":"helm_template","result":"simulated"},
    {"step":"meta_jobs_queued","count":1}
  ],
  "overall_status":"SIM_OK"
}
JSON

# Create an explainability stub
mkdir -p "${REPORTS}/explainability_reports"
cat > "${REPORTS}/explainability_reports/explainability_stub.json" <<JSON
{
  "id":"explain-stub-001",
  "created":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "top_features":["cpu_usage","latency","mem_usage"],
  "importance":[0.35,0.28,0.20],
  "notes":"Simulation stub"
}
JSON

echo "Deploy (simulation) wrote deploy_summary.json and explainability stub"