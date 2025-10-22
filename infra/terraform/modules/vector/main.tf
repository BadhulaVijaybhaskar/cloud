resource "kubernetes_namespace" "vector" {
  metadata {
    name = "vector"
  }
}

resource "helm_release" "milvus" {
  name       = "milvus"
  repository = "https://milvus-io.github.io/milvus-helm/"
  chart      = "milvus"
  namespace  = kubernetes_namespace.vector.metadata[0].name

  values = [
    file("../../helm/milvus/helm-values.yaml")
  ]
}

resource "kubernetes_deployment" "vector_api" {
  metadata {
    name      = "vector-api"
    namespace = kubernetes_namespace.vector.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "vector-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "vector-api"
        }
      }

      spec {
        container {
          image = "naksha/vector:latest"
          name  = "vector-api"

          port {
            container_port = 8081
          }

          env {
            name  = "MILVUS_HOST"
            value = "milvus"
          }

          env {
            name = "OPENAI_API_KEY"
            value_from {
              secret_key_ref {
                name = "openai-secret"
                key  = "api-key"
              }
            }
          }
        }
      }
    }
  }
}