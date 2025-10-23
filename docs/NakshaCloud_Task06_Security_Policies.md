# Naksha Cloud — Task 06: PodSecurity & NetworkPolicy

---

## Goal
Harden Naksha Cloud by enforcing non-root container execution and isolating network traffic between namespaces.

---

## 1. Pod Security Standards (Baseline or Restricted)

### Option A — Baseline (recommended for production)
`infra/security/podsecurity-baseline.yaml`
```yaml
apiVersion: policy/v1
kind: PodSecurityPolicy
metadata:
  name: naksha-baseline
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities: ["ALL"]
  runAsUser:
    rule: MustRunAsNonRoot
  seLinux:
    rule: RunAsAny
  fsGroup:
    rule: MustRunAs
    ranges:
      - min: 1
        max: 65535
  supplementalGroups:
    rule: MustRunAs
    ranges:
      - min: 1
        max: 65535
  readOnlyRootFilesystem: true
  volumes:
  - configMap
  - secret
  - projected
  - persistentVolumeClaim
```

Apply:

```bash
kubectl apply -f infra/security/podsecurity-baseline.yaml
```

> If PSP admission is not enabled, skip this and use PodSecurity admission labels (below).

### Option B — PodSecurity Admission Labels (modern clusters)

Label namespaces to **restricted** policy:

```bash
kubectl label ns langgraph pod-security.kubernetes.io/enforce=restricted --overwrite
kubectl label ns vector pod-security.kubernetes.io/enforce=restricted --overwrite
kubectl label ns vault pod-security.kubernetes.io/enforce=restricted --overwrite
```

---

## 2. NetworkPolicy — restrict inter-namespace access

### LangGraph Namespace Policy

`infra/security/langgraph-networkpolicy.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: langgraph-allow-vector-monitoring
  namespace: langgraph
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: vector
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
      - protocol: TCP
        port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: vector
    ports:
      - protocol: TCP
        port: 8081
```

### Vector Namespace Policy

`infra/security/vector-networkpolicy.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vector-allow-langgraph-monitoring
  namespace: vector
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: langgraph
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
      - protocol: TCP
        port: 8081
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
      - protocol: TCP
        port: 9090
```

Apply:

```bash
kubectl apply -f infra/security/langgraph-networkpolicy.yaml
kubectl apply -f infra/security/vector-networkpolicy.yaml
```

---

## 3. Verify Network Isolation

Run test pods:

```bash
kubectl run -n langgraph test-langgraph --image=busybox -- sleep 3600
kubectl run -n vector test-vector --image=busybox -- sleep 3600
```

### Positive test (allowed)

```bash
kubectl exec -n langgraph test-langgraph -- wget -qO- http://vector.vector.svc.cluster.local:8081/healthz
```

Expected: `{"status":"ok"}` ✅

### Negative test (blocked)

```bash
kubectl exec -n vault test-vault -- wget -qO- http://vector.vector.svc.cluster.local:8081/healthz
```

Expected: request **times out** ✅

Delete test pods:

```bash
kubectl delete pod -n langgraph test-langgraph
kubectl delete pod -n vector test-vector
kubectl delete pod -n vault test-vault
```

---

## 4. Verify Pod Security (non-root)

```bash
kubectl get pods -A -o=jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{" "}{.spec.containers[*].securityContext.runAsNonRoot}{"\n"}{end}'
```

Expected: all true or undefined (defaults to true).

---

## 5. Reporting & Artifacts

Agent must:

* Commit YAMLs under `infra/security/`
* Generate `/reports/security_policy.md` containing:

  * timestamp
  * `kubectl get networkpolicy -A`
  * connection-test results
  * output of pod-security checks
* Logs: `/reports/logs/security_apply.log`
* PR: `prod-hardening/06-security-policies`

---

## 6. Success Criteria

✅ NetworkPolicies restrict traffic correctly
✅ Monitoring namespace still accesses `/metrics`
✅ All pods run as non-root, read-only FS enforced
✅ Reports and PR created