# Naksha Cloud — Full Service Deployment & Visualization Setup

## **Goal**

Deploy the actual Naksha Cloud services (LangGraph, VectorDB, Vault, Observability) using proper Docker builds and Helm charts on the connected **Kubernetes v1.34.1** cluster.

## **1. Verify Environment**

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -A
```

## **2. Build and Push Service Images**

### LangGraph
```bash
cd services/langgraph
docker build -t naksha/langgraph:latest .
```

### Vector Service
```bash
cd services/vector
docker build -t naksha/vector:latest .
```

## **3. Update Kubernetes Deployments**

```bash
kubectl set image deployment/langgraph langgraph=naksha/langgraph:latest -n langgraph
kubectl set image deployment/vector vector=naksha/vector:latest -n vector
```

## **4. Verify Service Endpoints**

```bash
kubectl get svc -A
kubectl port-forward svc/langgraph -n langgraph 8080:8080
```

## **5. Deploy Observability Stack**

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
```

## **6. Success Criteria**

| Check | Status |
|-------|--------|
| LangGraph pod running | ✅ |
| Vector pod running | ✅ |
| Grafana dashboard live | ✅ |
| `/ui` shows DAG | ✅ |
| All metrics visible | ✅ |