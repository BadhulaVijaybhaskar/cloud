#!/bin/bash
set -euo pipefail

REPORTS_PATH="${REPORTS_PATH:-reports/l1}"
K9_TELEMETRY="${K9_TELEMETRY_PATH:-reports/k9/telemetry.json}"

echo "Running L.1 Post-Integration Audit..."
mkdir -p "$REPORTS_PATH"

# Generate K.9 telemetry if missing
if [ ! -f "$K9_TELEMETRY" ]; then
    echo "Generating K.9 telemetry data..."
    python services/k9-agent-core/telemetry/telemetry_collector.py
fi

# Run audit engine
python services/l1-audit-engine/src/main.py &
AUDIT_PID=$!
sleep 2

# Trigger audit
curl -s http://localhost:8810/v1/audit > "$REPORTS_PATH/audit_response.json"

# Stop audit engine
kill $AUDIT_PID 2>/dev/null || true

echo "Audit complete -> $REPORTS_PATH/post_integration_audit.json"