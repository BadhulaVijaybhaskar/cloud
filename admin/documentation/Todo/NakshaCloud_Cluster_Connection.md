

# Naksha Cloud — Cluster Connection and Validation

---

## **Goal**

Link the running local kubeadm v1.34.1 cluster with Naksha Cloud’s Terraform + Helm stack and validate readiness before deployment.

---

## **1. Validate Kubernetes Access**

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -A
```

Expected output:

```
NAME           STATUS   ROLES           VERSION
<hostname>     Ready    control-plane   v1.34.1
```

---

## **2. Verify Context Configuration**

```bash
kubectl config view --minify
kubectl config current-context
```

If not using default:

```bash
kubectl config use-context kubernetes-admin@kubernetes
```

---

## **3. Export kubeconfig for Terraform**

```bash
cat ~/.kube/config | base64 > infra/terraform/kubeconfig.b64
```

or on macOS:

```bash
cat ~/.kube/config | base64 | pbcopy
```

Then add to environment:

```bash
export KUBECONFIG_BASE64=$(cat infra/terraform/kubeconfig.b64)
```

---

## **4. Check Helm + Terraform CLI Access**

```bash
helm version
terraform version
```

If both respond correctly → environment is ready.

---

## **5. Preflight Cluster Validation Script**

`infra/scripts/check_cluster.sh`

```bash
#!/bin/bash
echo "Checking cluster state..."
kubectl get nodes -o wide
echo
kubectl get ns
echo
kubectl get cs
echo
kubectl get pods -A | grep -v "Running"
```

Expected: all system pods in `Running` or `Completed`.

---

## **6. Create Naksha Cloud Namespaces**

```bash
kubectl create ns langgraph
kubectl create ns vector
kubectl create ns vault
kubectl create ns monitoring
kubectl create ns realtime
```

Confirm:

```bash
kubectl get ns
```

---

## **7. Initialize Helm Dependencies**

```bash
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

---

## **8. Apply Terraform Infrastructure**

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply -auto-approve
```

Expected output:

```
Apply complete! Resources: <count> added.
```

---

## **9. Deploy Core Naksha Cloud Components**

```bash
helm upgrade --install langgraph infra/helm/langgraph -n langgraph
helm upgrade --install vector infra/helm/milvus -n vector
helm upgrade --install vault infra/vault -n vault
helm upgrade --install observability infra/helm/observability -n monitoring
```

Verify:

```bash
kubectl get pods -A
```

---

## **10. Integration Health Checks**

```bash
bash infra/scripts/test_health.sh
```

Expected:

```
LangGraph health: {"status":"ok"}
Vector health: {"status":"healthy"}
Vault: Initialized true, Sealed false
```

---

## **11. Proceed to Integration Testing**

After all pods are Running:

```bash
bash infra/scripts/setup.sh
bash infra/scripts/test_health.sh
```

Then follow:
`/docs/NakshaCloud_Integration_Testing.md`

---

## **12. Success Criteria**

| Check                          | Expected |
| ------------------------------ | -------- |
| Cluster reachable              | ✅        |
| Namespaces created             | ✅        |
| Helm charts deployed           | ✅        |
| All pods Running               | ✅        |
| LangGraph /healthz returns 200 | ✅        |
| Vault initialized              | ✅        |

---

### ✅ Result

When all checks pass, Naksha Cloud is now **connected to the kubeadm cluster** and ready for the **full integration test re-run**.
