#!/usr/bin/env bash
set -euo pipefail

ALERTMANAGER_URL="${ALERTMANAGER_URL:-http://localhost:9093}"
SIMULATION_MODE="${SIMULATION_MODE:-true}"
DRYRUN_POST="${DRYRUN_POST:-false}"

ALERT_NAME="L3ServiceDownTest"
INSTANCE="l3-orchestrator-dryrun"
SEVERITY="critical"
DESCRIPTION="Dry-run check: simulate L3 service down for alert routing verification."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

payload=$(cat <<JSON
[
  {
    "labels": {
      "alertname": "${ALERT_NAME}",
      "severity": "${SEVERITY}",
      "instance": "${INSTANCE}",
      "team": "l3-ops"
    },
    "annotations": {
      "summary": "${DESCRIPTION}",
      "runbook": "docs/runbooks/l3_runbook.md"
    },
    "startsAt": "${TIMESTAMP}",
    "generatorURL": "https://simulator.local/l3/alert_dryrun"
  }
]
JSON
)

echo "Alert dry-run payload:"
echo "${payload}"

if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "[SIMULATION] Not posting to Alertmanager. Use SIMULATION_MODE=false and DRYRUN_POST=true to actually send."
  exit 0
fi

if [ "${DRYRUN_POST}" != "true" ]; then
  echo "DRYRUN_POST is not set to true; aborting real post."
  exit 1
fi

echo "Posting to Alertmanager at ${ALERTMANAGER_URL}..."
curl -sS -XPOST -H 'Content-Type: application/json' --data "${payload}" "${ALERTMANAGER_URL}/api/v1/alerts" \
  && echo "Posted; check PagerDuty/Slack for routing." || (echo "Post failed" && exit 1)

echo "Alert dry-run complete."