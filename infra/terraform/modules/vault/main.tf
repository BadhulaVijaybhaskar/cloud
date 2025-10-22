resource "kubernetes_namespace" "vault" {
  metadata {
    name = "vault"
  }
}

resource "helm_release" "vault" {
  name       = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"
  namespace  = kubernetes_namespace.vault.metadata[0].name

  values = [
    file("../../vault/helm-values.yaml")
  ]
}

resource "vault_auth_backend" "kubernetes" {
  type = "kubernetes"
}

resource "vault_kubernetes_auth_backend_config" "kubernetes" {
  backend                = vault_auth_backend.kubernetes.path
  kubernetes_host        = "https://kubernetes.default.svc.cluster.local"
  kubernetes_ca_cert     = file("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
  token_reviewer_jwt     = file("/var/run/secrets/kubernetes.io/serviceaccount/token")
  disable_iss_validation = "true"
}

resource "vault_policy" "langgraph" {
  name   = "langgraph"
  policy = file("../../vault/policies/langgraph.hcl")
}

resource "vault_kubernetes_auth_backend_role" "langgraph" {
  backend                          = vault_auth_backend.kubernetes.path
  role_name                        = "langgraph-role"
  bound_service_account_names      = ["langgraph-sa"]
  bound_service_account_namespaces = ["langgraph"]
  token_ttl                        = 3600
  token_policies                   = ["langgraph"]
}