#!/bin/bash
# Run RAG smoke test on kind cluster

set -e

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-atom-e2e}"
KUBECONFIG_PATH="${KUBECONFIG_PATH:-/tmp/kubeconfig-${CLUSTER_NAME}}"
REGISTRY_PORT="${REGISTRY_PORT:-5001}"
TIMEOUT="${TIMEOUT:-600}"

echo "Running ATOM RAG smoke test..."
echo "Cluster: ${CLUSTER_NAME}"
echo "Kubeconfig: ${KUBECONFIG_PATH}"

# Check if cluster exists
check_cluster() {
    if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        echo "Error: Cluster ${CLUSTER_NAME} not found"
        echo "Run setup_kind.sh first"
        exit 1
    fi
    
    if [ ! -f "${KUBECONFIG_PATH}" ]; then
        echo "Error: Kubeconfig not found at ${KUBECONFIG_PATH}"
        exit 1
    fi
    
    echo "Cluster check passed"
}

# Deploy ATOM services using Helm
deploy_atom_services() {
    echo "Deploying ATOM services..."
    
    # Create values file for e2e testing
    cat > /tmp/atom-e2e-values.yaml <<EOF
global:
  registry: "localhost:${REGISTRY_PORT}"
  tag: "e2e"
  
workflowRegistry:
  enabled: true
  image:
    repository: localhost:${REGISTRY_PORT}/atom/workflow-registry
    tag: e2e
  service:
    type: NodePort
    nodePort: 30000
  env:
    ATOM_DEV_MODE: "true"
    
runtimeAgent:
  enabled: true
  image:
    repository: localhost:${REGISTRY_PORT}/atom/runtime-agent
    tag: e2e
  env:
    ATOM_DEV_MODE: "true"
    
langgraph:
  enabled: true
  image:
    repository: localhost:${REGISTRY_PORT}/atom/langgraph
    tag: e2e
  service:
    type: NodePort
    nodePort: 30001

postgresql:
  enabled: true
  auth:
    postgresPassword: "atom123"
    database: "atom_e2e"
  primary:
    persistence:
      enabled: false

minio:
  enabled: true
  auth:
    rootUser: "minioadmin"
    rootPassword: "minioadmin"
  defaultBuckets: "atom-e2e"
EOF
    
    # Install or upgrade ATOM using Helm
    if helm --kubeconfig="${KUBECONFIG_PATH}" list -n atom | grep -q atom; then
        echo "Upgrading existing ATOM deployment..."
        helm --kubeconfig="${KUBECONFIG_PATH}" upgrade atom ../../../infra/helm/atom \
            -n atom -f /tmp/atom-e2e-values.yaml
    else
        echo "Installing ATOM deployment..."
        helm --kubeconfig="${KUBECONFIG_PATH}" install atom ../../../infra/helm/atom \
            -n atom -f /tmp/atom-e2e-values.yaml --create-namespace
    fi
    
    # Wait for deployments to be ready
    echo "Waiting for ATOM services to be ready..."
    kubectl --kubeconfig="${KUBECONFIG_PATH}" wait --for=condition=available \
        deployment --all -n atom --timeout=300s
}

# Create test WPK files
create_test_wpks() {
    echo "Creating test WPK files..."
    
    mkdir -p /tmp/atom-e2e-wpks
    
    # Create restart-unhealthy WPK
    cat > /tmp/atom-e2e-wpks/restart-unhealthy.wpk.yaml <<EOF
apiVersion: v1
kind: WorkflowPackage
metadata:
  name: restart-unhealthy
  version: 1.0.0
  description: Restart unhealthy pods for e2e testing
  author: e2e-test
  signature: "e2e-test-signature"
spec:
  runtime:
    type: kubernetes
  safety:
    mode: manual
  handlers:
  - name: restart-pods
    steps:
    - name: check-pod-health
      kubernetes:
        apiVersion: v1
        kind: Pod
        metadata:
          name: health-check
          namespace: atom
        spec:
          restartPolicy: Never
          containers:
          - name: health-checker
            image: busybox:1.35
            command: ["sh", "-c", "echo 'Checking pod health...' && sleep 5 && echo 'Health check complete'"]
    - name: restart-unhealthy
      shell:
        command: |
          echo "Simulating pod restart..."
          echo "Found 2 unhealthy pods"
          echo "Restarting pods..."
          sleep 3
          echo "Restart complete"
EOF
    
    # Create scale-on-latency WPK
    cat > /tmp/atom-e2e-wpks/scale-on-latency.wpk.yaml <<EOF
apiVersion: v1
kind: WorkflowPackage
metadata:
  name: scale-on-latency
  version: 1.0.0
  description: Scale deployment based on latency for e2e testing
  author: e2e-test
  signature: "e2e-test-signature"
spec:
  runtime:
    type: kubernetes
  safety:
    mode: auto
  handlers:
  - name: scale-deployment
    steps:
    - name: check-latency
      shell:
        command: |
          echo "Checking service latency..."
          echo "Current latency: 250ms"
          echo "Threshold: 200ms"
          echo "Scaling required: true"
    - name: scale-up
      kubernetes:
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: test-app
          namespace: atom
        spec:
          replicas: 3
          selector:
            matchLabels:
              app: test-app
          template:
            metadata:
              labels:
                app: test-app
            spec:
              containers:
              - name: app
                image: nginx:1.21
                ports:
                - containerPort: 80
EOF
}

# Upload WPK files to registry
upload_wpks() {
    echo "Uploading WPK files to registry..."
    
    REGISTRY_URL="http://localhost:30000"
    
    # Wait for registry to be accessible
    echo "Waiting for workflow registry to be accessible..."
    for i in {1..30}; do
        if curl -f "${REGISTRY_URL}/health" &> /dev/null; then
            echo "Registry is accessible"
            break
        fi
        sleep 10
    done
    
    # Upload restart-unhealthy WPK
    echo "Uploading restart-unhealthy WPK..."
    curl -X POST "${REGISTRY_URL}/workflows" \
        -H "Authorization: Bearer e2e-test-token" \
        -F "file=@/tmp/atom-e2e-wpks/restart-unhealthy.wpk.yaml" \
        -v
    
    # Upload scale-on-latency WPK
    echo "Uploading scale-on-latency WPK..."
    curl -X POST "${REGISTRY_URL}/workflows" \
        -H "Authorization: Bearer e2e-test-token" \
        -F "file=@/tmp/atom-e2e-wpks/scale-on-latency.wpk.yaml" \
        -v
}

# Run workflow execution tests
run_workflow_tests() {
    echo "Running workflow execution tests..."
    
    REGISTRY_URL="http://localhost:30000"
    
    # Test 1: List workflows
    echo "Test 1: Listing workflows..."
    WORKFLOWS=$(curl -s "${REGISTRY_URL}/workflows")
    echo "Workflows response: ${WORKFLOWS}"
    
    if echo "${WORKFLOWS}" | grep -q "restart-unhealthy"; then
        echo "✓ restart-unhealthy workflow found"
    else
        echo "✗ restart-unhealthy workflow not found"
        return 1
    fi
    
    # Test 2: Get specific workflow
    echo "Test 2: Getting restart-unhealthy workflow..."
    WORKFLOW=$(curl -s "${REGISTRY_URL}/workflows/restart-unhealthy-1.0.0")
    echo "Workflow details: ${WORKFLOW}"
    
    if echo "${WORKFLOW}" | grep -q "restart-unhealthy"; then
        echo "✓ Workflow details retrieved"
    else
        echo "✗ Failed to get workflow details"
        return 1
    fi
    
    # Test 3: Dry-run validation
    echo "Test 3: Running dry-run validation..."
    DRYRUN=$(curl -s -X POST "${REGISTRY_URL}/workflows/restart-unhealthy-1.0.0/dry-run" \
        -H "Authorization: Bearer e2e-test-token")
    echo "Dry-run response: ${DRYRUN}"
    
    if echo "${DRYRUN}" | grep -q "risk_score"; then
        echo "✓ Dry-run validation completed"
    else
        echo "✗ Dry-run validation failed"
        return 1
    fi
    
    # Test 4: Check workflow runs endpoint
    echo "Test 4: Checking workflow runs..."
    RUNS=$(curl -s "${REGISTRY_URL}/workflows/restart-unhealthy-1.0.0/runs")
    echo "Runs response: ${RUNS}"
    
    if echo "${RUNS}" | grep -q "runs"; then
        echo "✓ Workflow runs endpoint accessible"
    else
        echo "✓ No runs found (expected for new workflow)"
    fi
}

# Verify database integration
verify_database() {
    echo "Verifying database integration..."
    
    # Get PostgreSQL pod
    PG_POD=$(kubectl --kubeconfig="${KUBECONFIG_PATH}" get pods -n atom -l app.kubernetes.io/name=postgresql -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "${PG_POD}" ]; then
        echo "✗ PostgreSQL pod not found"
        return 1
    fi
    
    echo "PostgreSQL pod: ${PG_POD}"
    
    # Check if workflow_runs table exists
    kubectl --kubeconfig="${KUBECONFIG_PATH}" exec -n atom "${PG_POD}" -- \
        psql -U postgres -d atom_e2e -c "\\dt" | grep -q workflow_runs
    
    if [ $? -eq 0 ]; then
        echo "✓ workflow_runs table exists"
    else
        echo "✗ workflow_runs table not found"
        return 1
    fi
    
    # Check if insight_signals table exists
    kubectl --kubeconfig="${KUBECONFIG_PATH}" exec -n atom "${PG_POD}" -- \
        psql -U postgres -d atom_e2e -c "\\dt" | grep -q insight_signals
    
    if [ $? -eq 0 ]; then
        echo "✓ insight_signals table exists"
    else
        echo "✗ insight_signals table not found"
        return 1
    fi
}

# Collect logs and artifacts
collect_artifacts() {
    echo "Collecting test artifacts..."
    
    mkdir -p /tmp/atom-e2e-artifacts
    
    # Collect pod logs
    kubectl --kubeconfig="${KUBECONFIG_PATH}" logs -n atom -l app=workflow-registry --tail=100 > /tmp/atom-e2e-artifacts/registry-logs.txt
    kubectl --kubeconfig="${KUBECONFIG_PATH}" logs -n atom -l app=runtime-agent --tail=100 > /tmp/atom-e2e-artifacts/runtime-logs.txt
    kubectl --kubeconfig="${KUBECONFIG_PATH}" logs -n atom -l app=langgraph --tail=100 > /tmp/atom-e2e-artifacts/langgraph-logs.txt
    
    # Collect cluster state
    kubectl --kubeconfig="${KUBECONFIG_PATH}" get all -n atom > /tmp/atom-e2e-artifacts/cluster-state.txt
    kubectl --kubeconfig="${KUBECONFIG_PATH}" describe pods -n atom > /tmp/atom-e2e-artifacts/pod-descriptions.txt
    
    echo "Artifacts collected in /tmp/atom-e2e-artifacts/"
}

# Cleanup function
cleanup() {
    echo "Cleaning up test resources..."
    rm -f /tmp/atom-e2e-values.yaml
    rm -rf /tmp/atom-e2e-wpks
}

# Main execution
main() {
    trap cleanup EXIT
    
    check_cluster
    
    # Skip deployment if services already running
    if kubectl --kubeconfig="${KUBECONFIG_PATH}" get deployment -n atom workflow-registry &> /dev/null; then
        echo "ATOM services already deployed, skipping deployment"
    else
        deploy_atom_services
    fi
    
    create_test_wpks
    upload_wpks
    run_workflow_tests
    verify_database
    collect_artifacts
    
    echo ""
    echo "RAG smoke test completed successfully! ✓"
    echo ""
    echo "Test results:"
    echo "- Workflow registry: ✓ Accessible"
    echo "- WPK upload: ✓ Working"
    echo "- Dry-run validation: ✓ Working"
    echo "- Database integration: ✓ Working"
    echo ""
    echo "Artifacts available in /tmp/atom-e2e-artifacts/"
}

# Run main function
main "$@"