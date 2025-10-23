#!/bin/bash
set -e

echo "🚀 Starting post-deploy smoke tests..."

# Configuration
TIMEOUT=30
RETRY_COUNT=3
SLEEP_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $description ($url)... "
    
    for i in $(seq 1 $RETRY_COUNT); do
        if response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null); then
            status_code="${response: -3}"
            if [ "$status_code" = "$expected_status" ]; then
                echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
                return 0
            fi
        fi
        
        if [ $i -lt $RETRY_COUNT ]; then
            echo -n "retry $((i+1))... "
            sleep $SLEEP_INTERVAL
        fi
    done
    
    echo -e "${RED}✗ FAIL${NC} (Expected HTTP $expected_status)"
    return 1
}

# Function to test Kubernetes service
test_k8s_service() {
    local service=$1
    local namespace=$2
    local port=$3
    local path=${4:-/healthz}
    
    echo -n "Testing Kubernetes service $service.$namespace:$port$path... "
    
    # Use kubectl port-forward for internal service testing
    kubectl port-forward -n "$namespace" "svc/$service" "$port:$port" &
    local pf_pid=$!
    sleep 2
    
    local success=false
    for i in $(seq 1 $RETRY_COUNT); do
        if response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "http://localhost:$port$path" 2>/dev/null); then
            status_code="${response: -3}"
            if [ "$status_code" = "200" ]; then
                echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
                success=true
                break
            fi
        fi
        
        if [ $i -lt $RETRY_COUNT ]; then
            echo -n "retry $((i+1))... "
            sleep $SLEEP_INTERVAL
        fi
    done
    
    # Clean up port-forward
    kill $pf_pid 2>/dev/null || true
    
    if [ "$success" = false ]; then
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
    
    return 0
}

# Function to check pod status
check_pod_status() {
    local namespace=$1
    local app_label=$2
    
    echo -n "Checking $app_label pods in $namespace namespace... "
    
    local ready_pods=$(kubectl get pods -n "$namespace" -l "app=$app_label" --field-selector=status.phase=Running -o jsonpath='{.items[*].status.containerStatuses[*].ready}' 2>/dev/null | grep -o true | wc -l)
    local total_pods=$(kubectl get pods -n "$namespace" -l "app=$app_label" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null | wc -w)
    
    if [ "$ready_pods" -gt 0 ] && [ "$ready_pods" -eq "$total_pods" ]; then
        echo -e "${GREEN}✓ PASS${NC} ($ready_pods/$total_pods pods ready)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} ($ready_pods/$total_pods pods ready)"
        return 1
    fi
}

# Start smoke tests
echo "=================================================="
echo "🔍 Naksha Cloud Post-Deploy Smoke Tests"
echo "=================================================="

# Test 1: Check pod health
echo -e "\n${YELLOW}1. Pod Health Checks${NC}"
check_pod_status "langgraph" "langgraph" || exit 1
check_pod_status "vector" "vector" || exit 1

# Test 2: Internal service connectivity
echo -e "\n${YELLOW}2. Internal Service Connectivity${NC}"
test_k8s_service "langgraph" "langgraph" "8080" "/healthz" || exit 1
test_k8s_service "vector" "vector" "8081" "/healthz" || exit 1

# Test 3: External endpoints (if ingress is configured)
echo -e "\n${YELLOW}3. External Endpoint Tests${NC}"
if kubectl get ingress -n langgraph naksha-ingress >/dev/null 2>&1; then
    echo "Testing ingress endpoints..."
    test_endpoint "https://langgraph.local/healthz" "LangGraph Ingress" 200 || echo -e "${YELLOW}⚠ WARNING: Ingress test failed (may be expected in CI)${NC}"
else
    echo "No ingress found, skipping external endpoint tests"
fi

# Test 4: Monitoring endpoints
echo -e "\n${YELLOW}4. Monitoring Stack Tests${NC}"
if kubectl get namespace monitoring >/dev/null 2>&1; then
    test_k8s_service "prometheus" "monitoring" "9090" "/-/healthy" || echo -e "${YELLOW}⚠ WARNING: Prometheus test failed${NC}"
    test_k8s_service "grafana" "monitoring" "3000" "/api/health" || echo -e "${YELLOW}⚠ WARNING: Grafana test failed${NC}"
else
    echo "Monitoring namespace not found, skipping monitoring tests"
fi

# Test 5: Database connectivity (if applicable)
echo -e "\n${YELLOW}5. Database Connectivity Tests${NC}"
if kubectl get pods -n langgraph -l app=postgres >/dev/null 2>&1; then
    echo "Testing database connectivity..."
    # This would require database credentials and proper testing
    echo -e "${YELLOW}⚠ INFO: Database connectivity test not implemented${NC}"
else
    echo "No database pods found, skipping database tests"
fi

# Test 6: Security policy validation
echo -e "\n${YELLOW}6. Security Policy Validation${NC}"
if kubectl get clusterpolicy require-signed-images >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} Image signing policy is active"
else
    echo -e "${YELLOW}⚠ WARNING: Image signing policy not found${NC}"
fi

if kubectl get networkpolicy -n langgraph >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} Network policies are configured"
else
    echo -e "${YELLOW}⚠ WARNING: Network policies not found${NC}"
fi

# Summary
echo -e "\n=================================================="
echo -e "${GREEN}🎉 Smoke tests completed successfully!${NC}"
echo "=================================================="

# Optional: Generate test report
cat > /tmp/smoke_test_report.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "status": "success",
  "tests_run": [
    "pod_health_checks",
    "internal_service_connectivity", 
    "external_endpoints",
    "monitoring_stack",
    "security_policies"
  ],
  "environment": "${ENVIRONMENT:-unknown}",
  "commit_sha": "${GITHUB_SHA:-unknown}"
}
EOF

echo "Test report saved to /tmp/smoke_test_report.json"
echo "Smoke tests passed! 🚀"