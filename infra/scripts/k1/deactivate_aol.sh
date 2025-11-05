#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-atom-auto}"
REPORT_DIR="reports/k1"
mkdir -p "${REPORT_DIR}"

echo "[K1] Deactivating Autonomous Runtime" | tee -a "${REPORT_DIR}/deactivate.log"

# Scale down AOL services
echo "[K1] Scaling down AOL services..." | tee -a "${REPORT_DIR}/deactivate.log"
kubectl scale deployment aol-controller --replicas=0 -n "${NAMESPACE}" || true
kubectl scale deployment aol-policy --replicas=0 -n "${NAMESPACE}" || true
kubectl scale deployment aol-executor --replicas=0 -n "${NAMESPACE}" || true
kubectl scale deployment aol-simulator --replicas=0 -n "${NAMESPACE}" || true

# Wait for pods to terminate
echo "[K1] Waiting for pods to terminate..." | tee -a "${REPORT_DIR}/deactivate.log"
kubectl wait --for=delete pod -l app.kubernetes.io/name=aol -n "${NAMESPACE}" --timeout=300s || true

# Generate deactivation report
cat > "${REPORT_DIR}/deactivation_summary.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "deactivated",
  "services_scaled_down": ["aol-controller", "aol-policy", "aol-executor", "aol-simulator"],
  "namespace": "${NAMESPACE}"
}
EOF

echo "[K1] AOL deactivation complete" | tee -a "${REPORT_DIR}/deactivate.log"