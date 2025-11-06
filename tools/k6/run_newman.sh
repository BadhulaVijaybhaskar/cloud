#!/usr/bin/env bash
set -e
COLL="tools/k6/k6_contract_collection.json"
REPORT_DIR="reports/k6"
mkdir -p $REPORT_DIR
newman run "$COLL" \
  --env-var "orchestrator=${K6_ORCHESTRATOR:-http://localhost:8900}" \
  --env-var "policy=${K6_POLICY:-http://localhost:8903}" \
  --env-var "metadata=${K6_METADATA:-http://localhost:8902}" \
  --reporters cli,json \
  --reporter-json-export "$REPORT_DIR/newman_report.json"
echo "Newman run complete. Report: $REPORT_DIR/newman_report.json"