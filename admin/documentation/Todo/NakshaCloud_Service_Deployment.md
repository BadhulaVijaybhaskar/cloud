Excellent. You’ve fully completed the **Cluster Connection Phase** — the infrastructure layer is verified and stable.
Next, you’re ready to move into **Deployment Stabilization and Visual Verification** (LangGraph orchestration UI + real service images).

Here’s your next agent instruction file to automate this final setup.

---

### Save as

> `/docs/NakshaCloud_Service_Deployment.md`

---

# Naksha Cloud — Full Service Deployment & Visualization Setup

---

## **Goal**

Deploy the actual Naksha Cloud services (LangGraph, VectorDB, Vault, Observability) using proper Docker builds and Helm charts on the connected **Kubernetes v1.34.1** cluster.

---

## **1. Verify Environment**

Before deployment, ensure:

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -A
```

Expected:

```
docker-desktop   Ready   control-plane   v1.34.1
```

All system pods must show `Running` status.

---

## **2. Build and Push Service Images**

### LangGraph

```bash
cd services/langgraph
docker build -t naksha/langgraph:latest .
docker tag naksha/langgraph:latest <your-dockerhub-user>/langgraph:latest
docker push <your-dockerhub-user>/langgraph:latest
```

### Vector Service

```bash
cd services/vector
docker build -t naksha/vector:latest .
docker tag naksha/vector:latest <your-dockerhub-user>/vector:latest
docker push <your-dockerhub-user>/vector:latest
```

Confirm with:

```bash
docker images | grep naksha
```

---

## **3. Update Kubernetes Deployments**

### LangGraph

```bash
kubectl set image deployment/langgraph langgraph=<your-dockerhub-user>/langgraph:latest -n langgraph
```

### Vector

```bash
kubectl set image deployment/vector vector=<your-dockerhub-user>/vector:latest -n vector
```

Wait until pods restart:

```bash
kubectl get pods -A
```

All should return to `Running`.

---

## **4. Verify Service Endpoints**

```bash
kubectl get svc -A
```

Expected:

```
langgraph   ClusterIP   10.x.x.x   8080/TCP
vector      ClusterIP   10.x.x.x   19530/TCP
```

Check health endpoints:

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/ui
```

---

## **5. Deploy Observability Stack (Grafana + Prometheus)**

If Helm is still unavailable, apply manifests manually:

```bash
kubectl apply -f infra/helm/observability/prometheus-values.yaml -n monitoring
kubectl apply -f infra/helm/observability/grafana-values.yaml -n monitoring
kubectl apply -f infra/helm/observability/loki-values.yaml -n monitoring
```

Port-forward Grafana:

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
```

Visit:

```
http://localhost:3000
```

Login: `admin / admin`
Dashboard → LangGraph Overview

---

## **6. Visualize LangGraph Orchestration**

Forward the LangGraph API:

```bash
kubectl port-forward svc/langgraph -n langgraph 8080:8080
```

Open in browser:

```
http://localhost:8080/ui
```

View:

* Active jobs
* Graph DAG from `/graph_definitions/sample_rag.yaml`
* Node execution flow
* Logs & metrics (Prometheus integrated)

If you installed **LangGraph Studio**:

```bash
langgraph studio start --graph ./services/langgraph/graph_definitions/sample_rag.yaml
```

→ Opens a DAG canvas at `http://localhost:3001`

---

## **7. Optional Vault Enablement**

```bash
kubectl apply -f infra/vault/helm-values.yaml -n vault
kubectl exec -n vault deploy/vault -- vault status
```

Expected:
`Initialized true, Sealed false`

---

## **8. Validation Script**

`infra/scripts/deploy_validate.sh`

```bash
#!/bin/bash
echo "LangGraph Pods:" 
kubectl get pods -n langgraph
echo
echo "Vector Pods:" 
kubectl get pods -n vector
echo
curl -s http://localhost:8080/healthz
```

Expected:

```
{"status": "ok"}
```

---

## **9. Reporting**

Agent should generate:

| File                                    | Purpose                           |
| --------------------------------------- | --------------------------------- |
| `/reports/service_deployment_report.md` | Summarized pod and service states |
| `/reports/logs/langgraph_deploy.log`    | Deployment logs                   |
| `/reports/logs/vector_deploy.log`       | Image update logs                 |

---

## **10. Success Criteria**

| Check                             | Status |
| --------------------------------- | ------ |
| LangGraph pod running             | ✅      |
| Vector pod running                | ✅      |
| Grafana dashboard live            | ✅      |
| `/ui` shows DAG                   | ✅      |
| Vault initialized                 | ✅      |
| All metrics visible in Prometheus | ✅      |

---

### ✅ Final Outcome

When complete, you will have:

* Live LangGraph orchestration UI (`/ui`)
* Prometheus + Grafana dashboards
* Vector search service live
* Secrets integration ready
* Verified production-like environment

Naksha Cloud is now visually operational and fully integrated with Kubernetes orchestration.

---

```
