resource "kubernetes_namespace" "langgraph" {
  metadata {
    name = "langgraph"
  }
}

resource "kubernetes_service_account" "langgraph" {
  metadata {
    name      = "langgraph-sa"
    namespace = kubernetes_namespace.langgraph.metadata[0].name
  }
}

resource "kubernetes_secret" "langgraph_config" {
  metadata {
    name      = "langgraph-config"
    namespace = kubernetes_namespace.langgraph.metadata[0].name
  }

  data = {
    DATABASE_URL  = var.env.DATABASE_URL
    VECTOR_DB_URL = var.env.VECTOR_DB_URL
    VAULT_ADDR    = var.env.VAULT_ADDR
  }
}

resource "helm_release" "langgraph" {
  name       = "langgraph"
  namespace  = kubernetes_namespace.langgraph.metadata[0].name
  chart      = "../../helm/langgraph"

  values = [
    file("../../helm/langgraph/values.yaml")
  ]

  depends_on = [kubernetes_secret.langgraph_config]
}