# Naksha Cloud — Task 02: Prometheus Alerting + Alertmanager Setup

## **Goal**
Add production-grade alerting for LangGraph, Vector, Vault, and storage health.

## **1. Create PrometheusRule**

**File:** `infra/monitoring/prometheus-rules.yaml`

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
```

## **2. Configure Alertmanager**

**File:** `infra/monitoring/alertmanager.yaml`

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
```

## **3. Apply Manifests**

```bash
kubectl apply -f infra/monitoring/prometheus-rules.yaml -n monitoring
kubectl apply -f infra/monitoring/alertmanager.yaml -n monitoring
```

## **4. Verification**

```bash
kubectl get prometheusrule -n monitoring
kubectl logs -n monitoring deploy/prometheus-server | grep "alert"
```

## **5. Test Alert Trigger**

```bash
kubectl scale deploy/langgraph -n langgraph --replicas=0
sleep 120
kubectl scale deploy/langgraph -n langgraph --replicas=1
```

## **Success Criteria**

✅ Prometheus rules listed in UI
✅ Alertmanager config healthy
✅ Simulated alert fired and resolved
✅ Slack / PagerDuty integration functional