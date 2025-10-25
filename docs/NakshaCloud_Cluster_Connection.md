# Naksha Cloud — Cluster Connection and Validation

## **Goal**

Link the running local kubeadm v1.34.1 cluster with Naksha Cloud's Terraform + Helm stack and validate readiness before deployment.

## **1. Validate Kubernetes Access**

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -A
```

## **2. Verify Context Configuration**

```bash
kubectl config view --minify
kubectl config current-context
```

## **3. Export kubeconfig for Terraform**

```bash
cat ~/.kube/config | base64 > infra/terraform/kubeconfig.b64
export KUBECONFIG_BASE64=$(cat infra/terraform/kubeconfig.b64)
```

## **4. Check Helm + Terraform CLI Access**

```bash
helm version
terraform version
```

## **5. Preflight Cluster Validation Script**

```bash
bash infra/scripts/check_cluster.sh
```

## **6. Create Naksha Cloud Namespaces**

```bash
kubectl create ns langgraph
kubectl create ns vector
kubectl create ns vault
kubectl create ns monitoring
kubectl create ns realtime
```

## **7. Initialize Helm Dependencies**

```bash
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

## **8. Apply Terraform Infrastructure**

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply -auto-approve
```

## **9. Deploy Core Naksha Cloud Components**

```bash
helm upgrade --install langgraph infra/helm/langgraph -n langgraph
helm upgrade --install vector infra/helm/milvus -n vector
helm upgrade --install vault infra/vault -n vault
helm upgrade --install observability infra/helm/observability -n monitoring
```

## **10. Integration Health Checks**

```bash
bash infra/scripts/test_health.sh
```