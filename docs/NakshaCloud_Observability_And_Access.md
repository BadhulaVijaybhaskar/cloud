# Naksha Cloud — Observability Stack & External Access Setup

## **Goal**

Enable Prometheus + Grafana + Loki monitoring stack, expose LangGraph UI externally, and validate full visibility.

## **1. Confirm Cluster Health**

```bash
kubectl get nodes -o wide
kubectl get pods -A
```

## **2. Deploy Observability Stack**

### **Install Prometheus**
```bash
helm upgrade --install prometheus prometheus-community/prometheus -n monitoring --create-namespace
```

### **Install Grafana**
```bash
helm upgrade --install grafana grafana/grafana -n monitoring --set adminUser=admin --set adminPassword=admin
```

### **Install Loki**
```bash
helm upgrade --install loki grafana/loki -n monitoring
```

## **3. Expose Grafana & LangGraph**

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80 &
kubectl port-forward svc/langgraph -n langgraph 8080:8080 &
```

## **4. Add Grafana Data Sources**

- Prometheus: `http://prometheus-server.monitoring.svc.cluster.local`
- Loki: `http://loki.monitoring.svc.cluster.local`

## **5. Validate Metrics**

```bash
kubectl port-forward svc/prometheus-server -n monitoring 9090:80
```

## **Success Criteria**

| Check | Expected Result |
|-------|----------------|
| Grafana accessible on port 3000 | ✅ |
| LangGraph UI accessible on port 8080 | ✅ |
| Prometheus shows targets UP | ✅ |
| Loki collects logs | ✅ |