# Terraform RBAC scaffold - customize providers and data sources per cloud
variable "namespace" {
  type    = string
  default = "atom-k2-canary"
}

# NOTE: provider and kubernetes config must be set at root
resource "kubernetes_namespace" "k2_canary" {
  metadata {
    name = var.namespace
    labels = {
      "app" = "k2-adaptive-ops"
    }
  }
}

resource "kubernetes_service_account" "k2_deployer" {
  metadata {
    name      = "k2-deployer"
    namespace = kubernetes_namespace.k2_canary.metadata[0].name
  }
}

resource "kubernetes_role" "k2_deployer_role" {
  metadata {
    name      = "k2-deployer-role"
    namespace = kubernetes_namespace.k2_canary.metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "endpoints", "configmaps", "secrets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  rule {
    api_groups = ["autoscaling"]
    resources  = ["horizontalpodautoscalers"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
}

resource "kubernetes_role_binding" "k2_deployer_binding" {
  metadata {
    name      = "k2-deployer-binding"
    namespace = kubernetes_namespace.k2_canary.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.k2_deployer.metadata[0].name
    namespace = kubernetes_namespace.k2_canary.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.k2_deployer_role.metadata[0].name
  }
}