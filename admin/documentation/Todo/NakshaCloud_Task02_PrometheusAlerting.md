Correct approach. You’ll want a clear `.md` file in your repo so the coding agent treats it as the source of truth.
Here’s the file you should create:

---

### **File path:**

`/docs/NakshaCloud_Task02_PrometheusAlerting.md`

### **File content:**

````markdown
# Naksha Cloud — Task 02: Prometheus Alerting + Alertmanager Setup

---

## **Goal**
Add production-grade alerting for LangGraph, Vector, Vault, and storage health.

---

## **1. Create PrometheusRule**

**File:** `infra/monitoring/prometheus-rules.yaml`

Define these rules:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: naksha-alerts
  namespace: monitoring
spec:
  groups:
  - name: naksha.rules
    rules:
    - alert: LangGraphCrash
      expr: kube_pod_container_status_waiting_reason{namespace="langgraph", reason="CrashLoopBackOff"} > 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "LangGraph pod crash"
        description: "LangGraph pod is in CrashLoopBackOff state."
    - alert: LangGraphJobFailureRate
      expr: increase(langgraph_job_failures_total[5m]) > 0
      for: 1m
      labels:
        severity: warning
      annotations:
        summary: "LangGraph job failures detected"
        description: "LangGraph job failure count increased in the last 5 minutes."
    - alert: VectorQPSDrop
      expr: (rate(vector_query_total[10m]) / ignoring() vector_query_baseline_rate) < 0.5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Vector QPS dropped by >50%"
        description: "Vector service query throughput fell below 50% of baseline."
    - alert: PVCHighUsage
      expr: (kubelet_volume_stats_available_bytes / kubelet_volume_stats_capacity_bytes) < 0.2
      for: 3m
      labels:
        severity: critical
      annotations:
        summary: "PVC usage >80%"
        description: "Persistent Volume Claim running low on available space."
    - alert: VaultSealed
      expr: vault_sealed == 1
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Vault sealed"
        description: "Vault instance is sealed and needs unsealing."
````

---

## **2. Configure Alertmanager**

**File:** `infra/monitoring/alertmanager.yaml`

Use Slack and fallback routing.

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'slack'
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: ${SLACK_WEBHOOK_URL}
        send_resolved: true
        text: |
          *Alert:* {{ .CommonAnnotations.summary }}
          *Description:* {{ .CommonAnnotations.description }}
          *Severity:* {{ .CommonLabels.severity }}

  - name: 'pagerduty'
    pagerduty_configs:
      - routing_key: ${PAGERDUTY_KEY}
        severity: 'critical'

templates: []
```

---

## **3. Apply Manifests**

```bash
kubectl apply -f infra/monitoring/prometheus-rules.yaml -n monitoring
kubectl apply -f infra/monitoring/alertmanager.yaml -n monitoring
```

---

## **4. Verification**

Run:

```bash
kubectl get prometheusrule -n monitoring
kubectl logs -n monitoring deploy/prometheus-server | grep "alert"
```

In Prometheus UI:

* Go to **Status → Rules** → confirm all five rules appear.
* Check **Alerts** tab → ensure no errors.

In Alertmanager:

* Access `/api/v2/status` and verify Slack receiver is active.

---

## **5. Test Alert Trigger**

Simulate a crash:

```bash
kubectl scale deploy/langgraph -n langgraph --replicas=0
sleep 120
kubectl scale deploy/langgraph -n langgraph --replicas=1
```

Confirm alert triggered and then resolved.

---

## **6. Reporting**

1. Save verification results to `/reports/alerts_status.md`
2. Log outputs to `/reports/logs/alerts_apply.log`
3. Commit all manifests + report to branch `prod-hardening/02-alerting`
4. Open PR: **"prod-hardening: 02 Prometheus Alerting + Alertmanager"**

---

## **Success Criteria**

✅ Prometheus rules listed in UI
✅ Alertmanager config healthy
✅ Simulated alert fired and resolved
✅ Slack / PagerDuty integration functional

```

