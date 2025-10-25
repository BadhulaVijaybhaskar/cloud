# Naksha Cloud — Integration Testing & Validation Guide

*version: agent-execution steps, October 2025*

## **Purpose**

To verify that all Naksha Cloud core services (LangGraph, VectorDB, Vault, Observability, CI/CD) are deployed, reachable, and generating metrics.

## **1. Prerequisites**

| Requirement                | Description                                 |
| -------------------------- | ------------------------------------------- |
| Kubernetes cluster         | local (k3d / Minikube) or managed (EKS/GKE) |
| kubectl + helm + terraform | installed on runner                         |
| Docker daemon              | for builds                                  |
| Python ≥ 3.11              | for LangGraph client tests                  |
| `.env` file                | created from `.env.example`                 |
| Network                    | outbound HTTPS for API pulls                |

## **2. Environment Preparation**

```bash
git clone https://github.com/BadhulaVijaybhaskar/cloud.git
cd cloud

# Load env
cp .env.example .env
source .env
```

Check required variables:

```bash
echo $DATABASE_URL
echo $VECTOR_DB_URL
echo $VAULT_ADDR
echo $PROMETHEUS_ADDR
```

## **3. Infrastructure Bootstrapping**

### **3.1 Run setup script**

```bash
bash infra/scripts/setup.sh
```

### **3.2 Terraform apply**

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### **3.3 Helm deploy**

```bash
helm upgrade --install langgraph infra/helm/langgraph/ -n langgraph
helm upgrade --install milvus infra/helm/milvus/ -n vector
helm upgrade --install vault infra/vault/ -n vault
helm upgrade --install observability infra/helm/observability/ -n monitoring
```

## **4. Service Health Validation**

### **4.1 LangGraph**

```bash
kubectl get pods -n langgraph
curl -f http://langgraph.langgraph.svc.cluster.local:8080/healthz
```

### **4.2 VectorDB**

```bash
kubectl get pods -n vector
curl -f http://milvus.vector.svc.cluster.local:19530/api/v1/health
```

### **4.3 Vault**

```bash
kubectl exec -n vault deploy/vault -- vault status
```

## **5. Functional Test (RAG Workflow)**

```bash
curl -X POST http://langgraph.langgraph.svc.cluster.local:8080/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"graph_name": "sample_rag", "input_data": {"query": "test"}}'
```

## **6. Observability Verification**

### **6.1 Prometheus Targets**

```bash
kubectl port-forward svc/prometheus-server -n monitoring 9090:80
```

### **6.2 Grafana Dashboards**

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
```

## **7. CI/CD Smoke Run**

```bash
gh workflow run infra-ci.yaml
```

## **8. Success Criteria**

| Check                                     | Result |
| ----------------------------------------- | ------ |
| All pods in `Running` state               | ✅      |
| LangGraph `/healthz` returns 200          | ✅      |
| Milvus & Vault respond healthy            | ✅      |
| Grafana dashboards active                 | ✅      |
| Prometheus scrape shows LangGraph metrics | ✅      |
| CI/CD job passes                          | ✅      |