# L.6 Cognitive Resilience Terraform Module

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  description = "Kubernetes namespace for L.6 services"
  type        = string
  default     = "l6-cognitive-resilience"
}

variable "simulation_mode" {
  description = "Enable simulation mode"
  type        = bool
  default     = true
}

resource "kubernetes_namespace" "l6_namespace" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "l6-cognitive-resilience"
      "phase" = "L.6"
    }
  }
}

# L.6 Orchestrator Deployment
resource "kubernetes_deployment" "l6_orchestrator" {
  metadata {
    name      = "l6-orchestrator"
    namespace = kubernetes_namespace.l6_namespace.metadata[0].name
  }

  spec {
    replicas = var.simulation_mode ? 1 : 3

    selector {
      match_labels = {
        app = "l6-orchestrator"
      }
    }

    template {
      metadata {
        labels = {
          app = "l6-orchestrator"
        }
      }

      spec {
        container {
          image = "l6-orchestrator:latest"
          name  = "orchestrator"

          env {
            name  = "SIMULATION_MODE"
            value = tostring(var.simulation_mode)
          }

          port {
            container_port = 9200
          }
        }
      }
    }
  }
}

output "namespace" {
  value = kubernetes_namespace.l6_namespace.metadata[0].name
}