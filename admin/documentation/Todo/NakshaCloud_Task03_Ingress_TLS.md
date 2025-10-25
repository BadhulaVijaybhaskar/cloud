Create this file and give it to the agent.

**Path:** `/docs/NakshaCloud_Task03_Ingress_TLS.md`

````markdown
# Naksha Cloud — Task 03: Ingress + TLS (Ingress-nginx + cert-manager)

---

## Goal
Replace NodePorts with HTTPS ingress for LangGraph and Grafana. Issue TLS certs via cert-manager (Let's Encrypt or self-signed for dev).

---

## Assumptions / Secrets
- You have cluster-admin privileges.
- For Let's Encrypt you need DNS for the host(s) and access to create DNS A records.
- If external DNS is not available use self-signed ClusterIssuer for dev and update `/etc/hosts`.

Required secrets (if using Let's Encrypt):
- `EMAIL_LETSENCRYPT` (email for ACME)
- Optional: cloud DNS credentials (for DNS01), otherwise use HTTP01 with public IP.

---

## Hosts (edit to your domain)
Adjust these hostnames to your domain before applying:
- `langgraph.naksha.example.com`
- `grafana.naksha.example.com`

For local dev you may use:
- `langgraph.local`
- `grafana.local`

---

## 1. Install prerequisites (if not installed)

### ingress-nginx (Helm)
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx -n ingress --create-namespace
````

### cert-manager (recommended)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.crds.yaml
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade --install cert-manager jetstack/cert-manager -n cert-manager --create-namespace \
  --set installCRDs=false
```

Verify:

```bash
kubectl get pods -n ingress
kubectl get pods -n cert-manager
```

---

## 2. Create ClusterIssuer

### Option A — Let's Encrypt (production)

Edit `infra/kubernetes/clusterissuer-letsencrypt.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ${EMAIL_LETSENCRYPT}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
```

Apply:

```bash
kubectl apply -f infra/kubernetes/clusterissuer-letsencrypt.yaml
```

### Option B — Self-signed (dev)

`infra/kubernetes/clusterissuer-selfsigned.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
```

Apply:

```bash
kubectl apply -f infra/kubernetes/clusterissuer-selfsigned.yaml
```

For dev also create a `Certificate` that signs with `selfsigned-issuer` then use `Certificate` + `ClusterIssuer` to produce `Secret`.

---

## 3. Ingress resource (example)

Create `infra/kubernetes/ingress-prod.yaml` (edit hosts):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: naksha-ingress
  namespace: langgraph
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod" # or selfsigned-issuer
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  tls:
    - hosts:
        - langgraph.naksha.example.com
        - grafana.naksha.example.com
      secretName: naksha-tls
  rules:
    - host: langgraph.naksha.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: langgraph
                port:
                  number: 8080
    - host: grafana.naksha.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: grafana
                port:
                  number: 80
```

Apply:

```bash
kubectl apply -f infra/kubernetes/ingress-prod.yaml
```

---

## 4. Local /etc/hosts mapping (for dev without DNS)

Find ingress controller IP:

```bash
kubectl get svc -n ingress ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# If using NodePort or Docker Desktop use host IP (127.0.0.1) or minikube ip
```

Edit `/etc/hosts` (example for localhost dev):

```bash
sudo -- sh -c "echo '127.0.0.1 langgraph.local grafana.local' >> /etc/hosts"
```

Or map to the ingress IP:

```bash
sudo -- sh -c "echo '<INGRESS_IP> langgraph.naksha.example.com grafana.naksha.example.com' >> /etc/hosts"
```

---

## 5. Verification

### Check ingress & certs

```bash
kubectl get ingress -n langgraph
kubectl describe ingress naksha-ingress -n langgraph
kubectl get certificates -A        # cert-manager resources
kubectl get orders -A
kubectl get challenges -A
kubectl describe certificate naksha-tls -n langgraph
kubectl get secret naksha-tls -n langgraph
```

### Health checks (HTTPS)

```bash
# LangGraph
curl -k https://langgraph.naksha.example.com/healthz
# Grafana
curl -k https://grafana.naksha.example.com
```

Expected `200` / HTML dashboard.

### Certificate details

```bash
kubectl get secret naksha-tls -n langgraph -o yaml
kubectl get certificate naksha-tls -n langgraph -o yaml
```

---

## 6. Rollback / Cleanup

To remove ingress and certs:

```bash
kubectl delete -f infra/kubernetes/ingress-prod.yaml
kubectl delete -f infra/kubernetes/clusterissuer-letsencrypt.yaml
```

---

## 7. Reporting & Artifacts

Agent must produce and commit:

* `infra/kubernetes/ingress-prod.yaml`
* `infra/kubernetes/clusterissuer-*.yaml`
* `/reports/ingress_tls.md` including:

  * timestamp
  * commands run and outputs
  * certificate status
  * curl results
  * any DNS steps performed
* Logs: `/reports/logs/ingress_apply.log`

Open PR: `prod-hardening/03-ingress-tls` with changes and report.

---

## 8. Success Criteria

* Ingress exists and routes to LangGraph and Grafana.
* TLS certificate is issued (or self-signed for dev) and secret present.
* `curl -k https://langgraph.<host>/healthz` returns HTTP 200.
* PR created with reports and artifacts.

---

## Agent prompt (paste to coding agent)

```


---

**Notes**

* For production use the Let's Encrypt issuer and real DNS records. For local testing use self-signed issuer and `/etc/hosts`.
* If DNS or ACME challenges require cloud DNS access, mark Task 3 BLOCKED and document required credentials.

```

```
