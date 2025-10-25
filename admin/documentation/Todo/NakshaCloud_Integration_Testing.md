Below is a **ready-to-use agent instruction document**.
Save it in your repo as:

> `/docs/NakshaCloud_Integration_Testing.md`

This Markdown tells your coding agent *exactly* how to execute end-to-end integration testing for the MVP build you already have.
All commands are deterministic and environment-agnostic.

---

# Naksha Cloud — Integration Testing & Validation Guide

*version: agent-execution steps, October 2025*

---

## **Purpose**

To verify that all Naksha Cloud core services (LangGraph, VectorDB, Vault, Observability, CI/CD) are deployed, reachable, and generating metrics.

---

## **1. Prerequisites**

| Requirement                | Description                                 |
| -------------------------- | ------------------------------------------- |
| Kubernetes cluster         | local (k3d / Minikube) or managed (EKS/GKE) |
| kubectl + helm + terraform | installed on runner                         |
| Docker daemon              | for builds                                  |
| Python ≥ 3.11              | for LangGraph client tests                  |
| `.env` file                | created from `.env.example`                 |
| Network                    | outbound HTTPS for API pulls                |

---

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

---

## **3. Infrastructure Bootstrapping**

### **3.1 Run setup script**

```bash
bash infra/scripts/setup.sh
```

This script initializes:

* Postgres schema and default data
* Object buckets
* Helm repos for Milvus, Vault, NATS
* Namespace creation

### **3.2 Terraform apply**

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

> Output should include `kubeconfig_raw` and deployed service endpoints.

### **3.3 Helm deploy**

```bash
helm upgrade --install langgraph infra/helm/langgraph/ -n langgraph
helm upgrade --install milvus infra/helm/milvus/ -n vector
helm upgrade --install vault infra/vault/ -n vault
helm upgrade --install observability infra/helm/observability/ -n monitoring
```

---

## **4. Service Health Validation**

### **4.1 LangGraph**

```bash
kubectl get pods -n langgraph
curl -f http://langgraph.langgraph.svc.cluster.local:8080/healthz
```

Expected:
`{"status": "ok", "version": "<commit_sha>"}`

### **4.2 VectorDB**

```bash
kubectl get pods -n vector
curl -f http://milvus.vector.svc.cluster.local:19530/api/v1/health
```

Expected: HTTP 200 + JSON with `"status":"healthy"`.

### **4.3 Vault**

```bash
kubectl exec -n vault deploy/vault -- vault status
```

Expected: `Initialized true, Sealed false`.

### **4.4 NATS / Redis**

```bash
kubectl get pods -n realtime
kubectl logs -n realtime deploy/nats | grep "Server is ready"
```

---

## **5. Functional Test (RAG Workflow)**

1. Copy sample graph definition:

   ```bash
   cp services/langgraph/graph_definitions/sample_rag.yaml /tmp/test_rag.yaml
   ```
2. Submit job:

   ```bash
   curl -X POST http://langgraph.langgraph.svc.cluster.local:8080/v1/jobs \
     -H "Content-Type: application/x-yaml" \
     --data-binary @/tmp/test_rag.yaml
   ```
3. Fetch status:

   ```bash
   curl http://langgraph.langgraph.svc.cluster.local:8080/v1/jobs/<job_id>
   ```

   Expected: `"state":"completed"` and `"result":"success"`.

---

## **6. Observability Verification**

### **6.1 Prometheus Targets**

```bash
kubectl port-forward svc/prometheus-server -n monitoring 9090:80
# open http://localhost:9090/targets
```

Confirm:

* LangGraph `/metrics`
* Milvus exporter
* Postgres exporter
* NATS exporter

### **6.2 Grafana Dashboards**

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
# open http://localhost:3000
```

Login (`admin/admin` default).
Validate:

* **LangGraph → Job Latency (ms)**
* **VectorDB → Query Throughput**
* **DB → Connections & I/O**
* **Vault → Auth Latency**

### **6.3 Loki Logs**

```bash
kubectl port-forward svc/loki -n monitoring 3100:80
curl -G http://localhost:3100/loki/api/v1/query \
     --data-urlencode 'query={app="langgraph"}'
```

Expected: recent job logs visible.

---

## **7. CI/CD Smoke Run**

```bash
gh workflow run infra-ci.yaml
gh run list --limit 1
```

Confirm Terraform plan, Helm upgrade, and post-deploy health probes all pass.

---

## **8. Automated Validation Script**

`infra/scripts/test_health.sh`

```bash
#!/bin/bash
set -e
echo "LangGraph health:" $(curl -s http://langgraph.langgraph.svc.cluster.local:8080/healthz)
echo "Vector health:" $(curl -s http://milvus.vector.svc.cluster.local:19530/api/v1/health)
curl -s http://vault.vault.svc.cluster.local:8200/v1/sys/health | jq .
```

Expected exit 0.

---

## **9. Success Criteria**

| Check                                     | Result |
| ----------------------------------------- | ------ |
| All pods in `Running` state               | ✅      |
| LangGraph `/healthz` returns 200          | ✅      |
| Milvus & Vault respond healthy            | ✅      |
| Grafana dashboards active                 | ✅      |
| Prometheus scrape shows LangGraph metrics | ✅      |
| CI/CD job passes                          | ✅      |

---

## **10. Cleanup (optional)**

```bash
helm uninstall langgraph -n langgraph
helm uninstall milvus -n vector
helm uninstall vault -n vault
helm uninstall observability -n monitoring
terraform destroy -auto-approve
```

---

### **Outcome**

When all tests complete:

* LangGraph workflows execute end-to-end.
* Metrics visible in Grafana.
* Logs searchable via Loki.
* All secrets served from Vault.

