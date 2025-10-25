#!/bin/bash
# Setup kind cluster for ATOM e2e testing

set -e

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-atom-e2e}"
KUBECONFIG_PATH="${KUBECONFIG_PATH:-/tmp/kubeconfig-${CLUSTER_NAME}}"
REGISTRY_PORT="${REGISTRY_PORT:-5001}"
TIMEOUT="${TIMEOUT:-300}"

echo "Setting up kind cluster for ATOM e2e testing..."
echo "Cluster name: ${CLUSTER_NAME}"
echo "Kubeconfig: ${KUBECONFIG_PATH}"

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    if ! command -v kind &> /dev/null; then
        echo "Error: kind is not installed"
        echo "Install with: go install sigs.k8s.io/kind@latest"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        echo "Error: kubectl is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "Error: docker is not installed"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo "Error: Docker daemon is not running"
        exit 1
    fi
    
    echo "Prerequisites check passed"
}

# Create kind cluster configuration
create_kind_config() {
    cat > /tmp/kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${CLUSTER_NAME}
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
    protocol: TCP
  - containerPort: 443
    hostPort: 8443
    protocol: TCP
  - containerPort: 30000
    hostPort: 30000
    protocol: TCP
  - containerPort: 30001
    hostPort: 30001
    protocol: TCP
- role: worker
  labels:
    atom-node: "true"
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:${REGISTRY_PORT}"]
    endpoint = ["http://registry:5000"]
EOF
}

# Create local registry
create_registry() {
    echo "Creating local Docker registry..."
    
    # Check if registry already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^registry$"; then
        echo "Registry container already exists, removing..."
        docker rm -f registry
    fi
    
    # Start registry
    docker run -d --restart=always -p "${REGISTRY_PORT}:5000" --name registry registry:2
    
    # Wait for registry to be ready
    echo "Waiting for registry to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:${REGISTRY_PORT}/v2/ &> /dev/null; then
            echo "Registry is ready"
            break
        fi
        sleep 2
    done
}

# Create kind cluster
create_cluster() {
    echo "Creating kind cluster..."
    
    # Delete existing cluster if it exists
    if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        echo "Cluster ${CLUSTER_NAME} already exists, deleting..."
        kind delete cluster --name "${CLUSTER_NAME}"
    fi
    
    # Create cluster
    kind create cluster --config /tmp/kind-config.yaml --kubeconfig "${KUBECONFIG_PATH}" --wait "${TIMEOUT}s"
    
    # Connect registry to cluster network
    docker network connect "kind" registry || true
    
    # Document the local registry
    kubectl --kubeconfig="${KUBECONFIG_PATH}" apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "localhost:${REGISTRY_PORT}"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
EOF
}

# Install ingress controller
install_ingress() {
    echo "Installing NGINX ingress controller..."
    
    kubectl --kubeconfig="${KUBECONFIG_PATH}" apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    # Wait for ingress controller to be ready
    echo "Waiting for ingress controller to be ready..."
    kubectl --kubeconfig="${KUBECONFIG_PATH}" wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=90s
}

# Create ATOM namespace and resources
setup_atom_namespace() {
    echo "Setting up ATOM namespace and resources..."
    
    kubectl --kubeconfig="${KUBECONFIG_PATH}" create namespace atom || true
    
    # Create service account for ATOM
    kubectl --kubeconfig="${KUBECONFIG_PATH}" apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: atom-sa
  namespace: atom
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: atom-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: atom-cluster-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: atom-cluster-role
subjects:
- kind: ServiceAccount
  name: atom-sa
  namespace: atom
EOF
    
    # Create resource quota
    kubectl --kubeconfig="${KUBECONFIG_PATH}" apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: atom-quota
  namespace: atom
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    services: "10"
    persistentvolumeclaims: "5"
EOF
}

# Build and push ATOM images
build_images() {
    echo "Building and pushing ATOM images..."
    
    # Build workflow registry image
    cd ../../../services/workflow-registry
    docker build -t localhost:${REGISTRY_PORT}/atom/workflow-registry:e2e .
    docker push localhost:${REGISTRY_PORT}/atom/workflow-registry:e2e
    
    # Build runtime agent image
    cd ../runtime-agent
    docker build -t localhost:${REGISTRY_PORT}/atom/runtime-agent:e2e .
    docker push localhost:${REGISTRY_PORT}/atom/runtime-agent:e2e
    
    # Build langgraph image
    cd ../langgraph
    docker build -t localhost:${REGISTRY_PORT}/atom/langgraph:e2e .
    docker push localhost:${REGISTRY_PORT}/atom/langgraph:e2e
    
    cd ../../tests/e2e/kind
}

# Verify cluster setup
verify_setup() {
    echo "Verifying cluster setup..."
    
    # Check nodes
    echo "Cluster nodes:"
    kubectl --kubeconfig="${KUBECONFIG_PATH}" get nodes
    
    # Check system pods
    echo "System pods:"
    kubectl --kubeconfig="${KUBECONFIG_PATH}" get pods -n kube-system
    
    # Check ATOM namespace
    echo "ATOM namespace resources:"
    kubectl --kubeconfig="${KUBECONFIG_PATH}" get all -n atom
    
    # Test registry connectivity
    echo "Testing registry connectivity..."
    if curl -f http://localhost:${REGISTRY_PORT}/v2/_catalog; then
        echo "Registry is accessible"
    else
        echo "Warning: Registry is not accessible"
    fi
}

# Cleanup function
cleanup() {
    echo "Cleaning up on exit..."
    if [ -f /tmp/kind-config.yaml ]; then
        rm -f /tmp/kind-config.yaml
    fi
}

# Main execution
main() {
    trap cleanup EXIT
    
    check_prerequisites
    create_kind_config
    create_registry
    create_cluster
    install_ingress
    setup_atom_namespace
    
    # Only build images if Docker files exist
    if [ -f "../../../services/workflow-registry/Dockerfile" ]; then
        build_images
    else
        echo "Skipping image build - Dockerfiles not found"
    fi
    
    verify_setup
    
    echo ""
    echo "Kind cluster setup completed successfully!"
    echo "Cluster name: ${CLUSTER_NAME}"
    echo "Kubeconfig: ${KUBECONFIG_PATH}"
    echo "Registry: localhost:${REGISTRY_PORT}"
    echo ""
    echo "To use this cluster:"
    echo "  export KUBECONFIG=${KUBECONFIG_PATH}"
    echo "  kubectl get nodes"
    echo ""
    echo "To cleanup:"
    echo "  kind delete cluster --name ${CLUSTER_NAME}"
    echo "  docker rm -f registry"
}

# Run main function
main "$@"