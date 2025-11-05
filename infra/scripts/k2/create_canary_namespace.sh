#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${1:-atom-k2-canary}
SIM=${SIMULATION_MODE:-true}

echo "Creating canary namespace: ${NAMESPACE} (SIMULATION_MODE=${SIM})"

if [ "${SIM}" = "true" ]; then
  echo "[SIMULATION] Namespace and RBAC will not be applied. Exiting (simulation mode)."
  exit 0
fi

kubectl create namespace "${NAMESPACE}" || echo "namespace ${NAMESPACE} exists"
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: k2-deployer
  namespace: ${NAMESPACE}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: k2-deployer-role
  namespace: ${NAMESPACE}
rules:
- apiGroups: ["", "apps", "autoscaling"]
  resources: ["pods","deployments","replicasets","horizontalpodautoscalers"]
  verbs: ["get","list","watch","create","update","patch","delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: k2-deployer-binding
  namespace: ${NAMESPACE}
subjects:
- kind: ServiceAccount
  name: k2-deployer
  namespace: ${NAMESPACE}
roleRef:
  kind: Role
  name: k2-deployer-role
  apiGroup: rbac.authorization.k8s.io
EOF

echo "Canary namespace '${NAMESPACE}' and RBAC created."