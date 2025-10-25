Excellent. Your **core services (LangGraph + Vector)** are live and verified — that’s the hardest part done.
Next phase: deploy **Observability + External Access**, so you can monitor metrics and open APIs externally.

Here’s your next agent document.

---

### Save as

> `/docs/NakshaCloud_Observability_And_Access.md`

---

# Naksha Cloud — Observability Stack & External Access Setup

---

## **Goal**

Enable Prometheus + Grafana + Loki monitoring stack, expose LangGraph UI externally (Ingress / LoadBalancer), and validate full visibility.

---

## **1. Confirm Cluster Health**

```bash
kubectl get nodes -o wide
kubectl get pods -A
```

All system and Naksha pods must show `STATUS=Running`.

---

## **2. Deploy Observability Stack**

If Helm is available:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### **Install Prometheus**

```bash
helm upgrade --install prometheus prometheus-community/prometheus -n monitoring \
  --create-namespace
```

### **Install Grafana**

```bash
helm upgrade --install grafana grafana/grafana -n monitoring \
  --set adminUser=admin --set adminPassword=admin
```

### **Install Loki (Logs)**

```bash
helm upgrade --install loki grafana/loki -n monitoring
```

---

## **3. Expose Grafana & LangGraph**

### Option A — Port-forward (local test)

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80 &
kubectl port-forward svc/langgraph -n langgraph 8080:8080 &
```

Visit:

* Grafana → `http://localhost:3000`
* LangGraph UI → `http://localhost:8080/ui`

---

### Option B — Kubernetes Ingress (external)

```bash
kubectl apply -f infra/kubernetes/ingress.yaml
```

Example ingress.yaml:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: naksha-ingress
  namespace: langgraph
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: naksha.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: langgraph
                port:
                  number: 8080
```

Update `/etc/hosts`:

```
127.0.0.1 naksha.local
```

Then open → `http://naksha.local/ui`

---

## **4. Add Grafana Data Sources**

1. Open Grafana → `http://localhost:3000`
   Login → **admin / admin**
2. Go to ⚙️ → Data Sources → Add new

   * **Prometheus:** `http://prometheus-server.monitoring.svc.cluster.local`
   * **Loki:** `http://loki.monitoring.svc.cluster.local`
3. Save & test connections.

---

## **5. Import Dashboards**

Import JSON dashboards from `/infra/helm/observability/`:

* **LangGraph Orchestration Overview**
* **Vector Query Metrics**
* **Vault Health**
* **Pod Resource Usage**

Run:

```bash
kubectl cp infra/helm/observability/dashboards grafana/<grafana-pod>:/var/lib/grafana/dashboards -n monitoring
```

---

## **6. Validate Metrics**

```bash
kubectl port-forward svc/prometheus-server -n monitoring 9090:80
```

Visit:

```
http://localhost:9090/targets
```

Confirm targets:

* langgraph:8080/metrics → `UP`
* vector:8081/metrics → `UP`
* vault:8200/sys/metrics → `UP`

---

## **7. Validate Logs via Loki**

```bash
kubectl logs -n langgraph -l app=langgraph --tail=50
```

In Grafana:

* Explore → Loki → `{namespace="langgraph"}` → query logs.

---

## **8. Integration Test (Monitoring + API)**

Run:

```bash
bash infra/scripts/test_health.sh
curl -f http://localhost:8080/healthz
```

Expected:

```
{"status": "ok"}
```

Then:

```bash
curl http://localhost:8080/v1/jobs
```

Expected list of jobs or empty array.

Grafana → Dashboard → Latency and Job count visible.

---

## **9. Report Generation**

Agent must output:

| File                                    | Description                             |
| --------------------------------------- | --------------------------------------- |
| `/reports/observability_report.md`      | Prometheus + Grafana validation summary |
| `/reports/logs/observability.log`       | Log capture of deployment and targets   |
| `/reports/screenshots/grafana_dash.png` | Screenshot of live dashboard            |

---

## **10. Success Criteria**

| Check                                          | Expected Result |
| ---------------------------------------------- | --------------- |
| Grafana accessible on port 3000                | ✅               |
| LangGraph UI accessible on port 8080 / Ingress | ✅               |
| Prometheus shows LangGraph, Vector targets UP  | ✅               |
| Loki collects logs from all pods               | ✅               |
| Dashboards display active metrics              | ✅               |

---

### ✅ **Final Output**

When all checks pass:

> Naksha Cloud observability and access layer deployed successfully.
> Metrics, logs, and orchestration graphs now visible through Grafana and LangGraph UI.

---

