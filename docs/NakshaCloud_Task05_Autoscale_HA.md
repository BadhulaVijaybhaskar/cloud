# Naksha Cloud — Task 05: Autoscaling, High Availability & Resource Limits

---

## Goal
Add autoscaling, PodDisruptionBudgets, and resource requests/limits to improve resilience and stability for LangGraph and Vector services.

---

## Assumptions
- Cluster supports HPA (metrics-server or kube-metrics installed).
- kubectl and helm access available.
- LangGraph deployment is in namespace `langgraph`.
- Vector deployment is in namespace `vector`.

---

## 1. Install Metrics Server (if missing)
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl get deployment metrics-server -n kube-system
```

---

## 2. Add resource requests/limits (Deployment patch examples)

Create file: `infra/kubernetes/langgraph-deployment-resources.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph
  namespace: langgraph
spec:
  template:
    spec:
      containers:
      - name: langgraph
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
```

Create file: `infra/kubernetes/vector-deployment-resources.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vector
  namespace: vector
spec:
  template:
    spec:
      containers:
      - name: vector
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
```

Apply (these are patches; use `kubectl apply -f` if your manifests are full deployments, or use `kubectl patch` for live deployments):

```bash
kubectl apply -f infra/kubernetes/langgraph-deployment-resources.yaml
kubectl apply -f infra/kubernetes/vector-deployment-resources.yaml
kubectl rollout restart deploy/langgraph -n langgraph
kubectl rollout restart deploy/vector -n vector
```

---

## 3. Create HorizontalPodAutoscaler (HPA)

### LangGraph HPA

File: `infra/kubernetes/langgraph-hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: langgraph-hpa
  namespace: langgraph
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: langgraph
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
```

### Vector HPA (CPU based)

File: `infra/kubernetes/vector-hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vector-hpa
  namespace: vector
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vector
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
```

Apply:

```bash
kubectl apply -f infra/kubernetes/langgraph-hpa.yaml
kubectl apply -f infra/kubernetes/vector-hpa.yaml
```

---

## 4. PodDisruptionBudget (PDB)

### LangGraph PDB

File: `infra/kubernetes/langgraph-pdb.yaml`

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: langgraph-pdb
  namespace: langgraph
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: langgraph
```

### Vector PDB

File: `infra/kubernetes/vector-pdb.yaml`

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: vector-pdb
  namespace: vector
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: vector
```

Apply:

```bash
kubectl apply -f infra/kubernetes/langgraph-pdb.yaml
kubectl apply -f infra/kubernetes/vector-pdb.yaml
```

---

## 5. Optional: Custom Metrics (Queue depth)

If you have a queue metric (NATS/Redis) exposed, use Kubernetes Metric Adapter or Prometheus Adapter to scale on queue depth. Document below if available:

* metric name: `queue_depth` (example)
* HPA metric snippet (v2 API) can use `type: External` to reference adapter metric.

If adapter not available, skip and rely on CPU scaling.

---

## 6. Verification

Run:

```bash
kubectl get hpa -n langgraph -o wide
kubectl get hpa -n vector -o wide

kubectl describe hpa langgraph-hpa -n langgraph
kubectl describe hpa vector-hpa -n vector

kubectl get pdb -n langgraph
kubectl get pdb -n vector

kubectl top pods -n langgraph
kubectl top pods -n vector
```

Simulate load (optional) to verify scaling:

```bash
# simple CPU burn to test autoscale on langgraph pods (run in a test pod)
kubectl run -n langgraph -i --tty loadgen --image=busybox -- /bin/sh
# inside pod: while true; do dd if=/dev/zero of=/dev/null bs=1M count=1024; done
```

Observe HPA scaling:

```bash
kubectl get pods -n langgraph --watch
```

---

## 7. Reporting & Artifacts

Agent must:

* Commit `infra/kubernetes/*.yaml` files to branch `prod-hardening/05-autoscale-ha`
* Open PR titled: `prod-hardening: 05 autoscale & HA`
* Save verification output to `/reports/hpa_pdb.md`
* Save logs to `/reports/logs/hpa_apply.log`

`/reports/hpa_pdb.md` must include:

* timestamp
* `kubectl get hpa` output
* `kubectl describe hpa <name>` output
* `kubectl get pdb` output
* result of `kubectl top pods` snapshot
* any errors and remediation steps

---

## 8. Success Criteria

* HPAs created for langgraph and vector and `kubectl get hpa` shows min/max replicas. ✅
* PodDisruptionBudgets present and bound. ✅
* Resource requests/limits applied and pods restarted successfully. ✅
* HPA responds to load or reports metrics available. ✅
* Artifacts committed and PR opened. ✅