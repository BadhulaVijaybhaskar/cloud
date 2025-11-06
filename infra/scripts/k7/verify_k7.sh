#!/usr/bin/env bash
set -e
REPORTS="reports/k7"
mkdir -p "${REPORTS}"
echo "Verifying K.7 (SIMULATION_MODE=${SIMULATION_MODE:-true})"
if [ ! -f "${REPORTS}/precheck_report.json" ]; then
  echo "precheck_report.json missing"; exit 1
fi
if [ ! -f "${REPORTS}/deploy_summary.json" ]; then
  echo "deploy_summary.json missing"; exit 1
fi

jq -s 'reduce .[] as $item ({}; . * $item)' ${REPORTS}/*.json > ${REPORTS}/verification_summary.json || true
echo "Verification summary written to ${REPORTS}/verification_summary.json"