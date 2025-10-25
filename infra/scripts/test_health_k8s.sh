#!/bin/bash
set -e

echo "=== Naksha Cloud Kubernetes Health Check ==="
echo "Timestamp: $(date)"

# Check Kubernetes cluster
echo "Checking Kubernetes cluster..."
kubectl cluster-info

# Check namespaces
echo "Checking namespaces..."
kubectl get ns

# Check pod status
echo "Checking pod status..."
kubectl get pods -A

# Check services
echo "Checking services..."
kubectl get svc -A

# Test LangGraph pod
echo "Testing LangGraph pod..."
if kubectl get pod -n langgraph -l app=langgraph | grep Running > /dev/null; then
    echo "[OK] LangGraph: Pod running"
else
    echo "[FAIL] LangGraph: Pod not running"
fi

# Test Vector pod
echo "Testing Vector pod..."
if kubectl get pod -n vector -l app=vector | grep Running > /dev/null; then
    echo "[OK] Vector: Pod running"
else
    echo "[FAIL] Vector: Pod not running"
fi

echo "=== Health Check Complete ==="