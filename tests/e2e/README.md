# ATOM End-to-End Testing

## Overview

This directory contains end-to-end (e2e) tests for the ATOM platform using kind (Kubernetes in Docker) for local testing and CI/CD pipelines.

## Prerequisites

### Required Tools
- **Docker**: Container runtime
- **kind**: Kubernetes in Docker (`go install sigs.k8s.io/kind@latest`)
- **kubectl**: Kubernetes CLI
- **helm**: Kubernetes package manager
- **curl**: HTTP client for API testing

### System Requirements
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **CPU**: Minimum 4 cores
- **Disk**: Minimum 20GB free space
- **OS**: Linux, macOS, or Windows with WSL2

## Quick Start

### 1. Setup Kind Cluster
```bash
cd tests/e2e/kind
./setup_kind.sh
```

This will:
- Create a kind cluster named `atom-e2e`
- Set up local Docker registry
- Install NGINX ingress controller
- Create ATOM namespace and RBAC
- Build and push ATOM images (if Dockerfiles exist)

### 2. Run Smoke Tests
```bash
./run_rag_smoke.sh
```

This will:
- Deploy ATOM services using Helm
- Upload test WPK packages
- Run workflow API tests
- Verify database integration
- Collect test artifacts

### 3. Cleanup
```bash
kind delete cluster --name atom-e2e
docker rm -f registry
```

## Test Structure

### Kind Cluster Tests
- **setup_kind.sh**: Creates isolated Kubernetes cluster
- **run_rag_smoke.sh**: Runs comprehensive smoke tests
- **deploy_minikube.sh**: Alternative deployment for Minikube (future)

### Test Scenarios

#### Smoke Tests
1. **Service Deployment**: Verify all ATOM services start correctly
2. **API Connectivity**: Test workflow registry endpoints
3. **WPK Upload**: Upload and validate workflow packages
4. **Dry-Run Validation**: Test static validation and policy engine
5. **Database Integration**: Verify PostgreSQL tables and data
6. **Storage Integration**: Test MinIO/S3 connectivity

#### Integration Tests
1. **Workflow Execution**: End-to-end workflow runs
2. **Cross-Service Communication**: Registry ↔ Runtime Agent ↔ LangGraph
3. **Monitoring Integration**: Prometheus metrics collection
4. **Security Validation**: Cosign signature verification
5. **Vault Integration**: Secret management (if configured)

## Configuration

### Environment Variables
```bash
# Cluster configuration
export CLUSTER_NAME="atom-e2e"
export KUBECONFIG_PATH="/tmp/kubeconfig-atom-e2e"
export REGISTRY_PORT="5001"
export TIMEOUT="600"

# Service configuration
export ATOM_DEV_MODE="true"
export POSTGRES_PASSWORD="atom123"
export MINIO_ROOT_PASSWORD="minioadmin"
```

### Helm Values
The e2e tests use custom Helm values optimized for testing:

```yaml
global:
  registry: "localhost:5001"
  tag: "e2e"

workflowRegistry:
  service:
    type: NodePort
    nodePort: 30000
  env:
    ATOM_DEV_MODE: "true"

postgresql:
  auth:
    postgresPassword: "atom123"
  primary:
    persistence:
      enabled: false  # Ephemeral storage for testing

minio:
  auth:
    rootPassword: "minioadmin"
  defaultBuckets: "atom-e2e"
```

## Test WPK Packages

### restart-unhealthy.wpk.yaml
```yaml
apiVersion: v1
kind: WorkflowPackage
metadata:
  name: restart-unhealthy
  version: 1.0.0
  description: Restart unhealthy pods for e2e testing
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
        # Pod health check configuration
    - name: restart-unhealthy
      shell:
        command: "echo 'Simulating pod restart...'"
```

### scale-on-latency.wpk.yaml
```yaml
apiVersion: v1
kind: WorkflowPackage
metadata:
  name: scale-on-latency
  version: 1.0.0
  description: Scale deployment based on latency
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
        command: "echo 'Checking service latency...'"
    - name: scale-up
      kubernetes:
        # Deployment scaling configuration
```

## API Testing

### Workflow Registry Endpoints
```bash
# Health check
curl http://localhost:30000/health

# List workflows
curl http://localhost:30000/workflows

# Get specific workflow
curl http://localhost:30000/workflows/restart-unhealthy-1.0.0

# Upload WPK
curl -X POST http://localhost:30000/workflows \
  -H "Authorization: Bearer test-token" \
  -F "file=@restart-unhealthy.wpk.yaml"

# Dry-run validation
curl -X POST http://localhost:30000/workflows/restart-unhealthy-1.0.0/dry-run \
  -H "Authorization: Bearer test-token"

# Get workflow runs
curl http://localhost:30000/workflows/restart-unhealthy-1.0.0/runs
```

### Expected Responses
- **Health Check**: `{"status": "healthy"}`
- **List Workflows**: `{"workflows": [...], "total": N}`
- **Dry-Run**: `{"validation": {...}, "risk_score": N}`

## Database Verification

### PostgreSQL Tables
```sql
-- Connect to database
kubectl exec -it postgresql-pod -- psql -U postgres -d atom_e2e

-- Check tables
\dt

-- Verify workflow_runs table
SELECT COUNT(*) FROM workflow_runs;

-- Verify insight_signals table
SELECT COUNT(*) FROM insight_signals;
```

### Expected Tables
- `workflow_runs`: Stores workflow execution history
- `insight_signals`: Stores anomaly detection signals
- `workflows`: Stores workflow metadata (if using DB storage)

## Troubleshooting

### Common Issues

#### 1. Kind Cluster Creation Fails
```bash
# Check Docker daemon
docker info

# Check available resources
docker system df

# Clean up existing resources
kind delete cluster --name atom-e2e
docker system prune -f
```

#### 2. Image Build/Push Fails
```bash
# Check registry connectivity
curl http://localhost:5001/v2/_catalog

# Manually build and push
cd services/workflow-registry
docker build -t localhost:5001/atom/workflow-registry:e2e .
docker push localhost:5001/atom/workflow-registry:e2e
```

#### 3. Service Deployment Issues
```bash
# Check pod status
kubectl get pods -n atom

# Check pod logs
kubectl logs -n atom deployment/workflow-registry

# Check events
kubectl get events -n atom --sort-by='.lastTimestamp'
```

#### 4. API Connectivity Issues
```bash
# Check service endpoints
kubectl get svc -n atom

# Port forward for debugging
kubectl port-forward -n atom svc/workflow-registry 8000:8000

# Test local connection
curl http://localhost:8000/health
```

### Debug Commands
```bash
# Cluster information
kubectl cluster-info --kubeconfig=/tmp/kubeconfig-atom-e2e

# Node status
kubectl get nodes -o wide

# All resources in atom namespace
kubectl get all -n atom

# Pod descriptions
kubectl describe pods -n atom

# Service endpoints
kubectl get endpoints -n atom

# Ingress status
kubectl get ingress -n atom
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Kind
      run: |
        cd tests/e2e/kind
        ./setup_kind.sh
    
    - name: Run Smoke Tests
      run: |
        cd tests/e2e/kind
        ./run_rag_smoke.sh
    
    - name: Collect Artifacts
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: e2e-artifacts
        path: /tmp/atom-e2e-artifacts/
    
    - name: Cleanup
      if: always()
      run: |
        kind delete cluster --name atom-e2e
        docker rm -f registry
```

### GitLab CI Example
```yaml
e2e-tests:
  stage: test
  image: ubuntu:22.04
  services:
    - docker:dind
  before_script:
    - apt-get update && apt-get install -y curl docker.io
    - curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
    - chmod +x ./kind && mv ./kind /usr/local/bin/
  script:
    - cd tests/e2e/kind
    - ./setup_kind.sh
    - ./run_rag_smoke.sh
  after_script:
    - kind delete cluster --name atom-e2e || true
    - docker rm -f registry || true
  artifacts:
    when: always
    paths:
      - /tmp/atom-e2e-artifacts/
    expire_in: 1 week
```

## Performance Testing

### Load Testing
```bash
# Install k6 for load testing
curl https://github.com/grafana/k6/releases/download/v0.46.0/k6-v0.46.0-linux-amd64.tar.gz -L | tar xvz --strip-components 1

# Run load test
./k6 run --vus 10 --duration 30s load-test.js
```

### Resource Monitoring
```bash
# Monitor cluster resources
kubectl top nodes
kubectl top pods -n atom

# Monitor registry performance
curl -s http://localhost:30000/metrics | grep http_requests_total
```

## Security Testing

### Vulnerability Scanning
```bash
# Scan container images
trivy image localhost:5001/atom/workflow-registry:e2e

# Scan Kubernetes manifests
trivy config infra/helm/
```

### Network Policy Testing
```bash
# Test network isolation
kubectl exec -n atom test-pod -- curl workflow-registry:8000/health

# Verify ingress rules
curl -H "Host: atom.local" http://localhost:8080/health
```

## Extending Tests

### Adding New Test Scenarios
1. Create new WPK test files in `/tmp/atom-e2e-wpks/`
2. Add upload logic to `run_rag_smoke.sh`
3. Implement test assertions
4. Update documentation

### Custom Test Environments
1. Modify `setup_kind.sh` configuration
2. Create custom Helm values files
3. Add environment-specific test cases
4. Document new requirements

## References

- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Kubernetes Testing Guide](https://kubernetes.io/docs/tasks/debug-application-cluster/debug-application/)
- [Helm Testing](https://helm.sh/docs/chart_tests/)
- [Container Testing Best Practices](https://testcontainers.org/)