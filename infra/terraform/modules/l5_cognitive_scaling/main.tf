# L.5 Cognitive Federation Scaling Terraform Module

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  description = "Kubernetes namespace for L.5 services"
  type        = string
  default     = "l5-cognitive-scaling"
}

variable "simulation_mode" {
  description = "Enable simulation mode"
  type        = bool
  default     = true
}

resource "kubernetes_namespace" "l5_namespace" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "l5-cognitive-scaling"
      "phase" = "L.5"
    }
  }
}

# L.5 Orchestrator Deployment
resource "kubernetes_deployment" "l5_orchestrator" {
  metadata {
    name      = "l5-orchestrator"
    namespace = kubernetes_namespace.l5_namespace.metadata[0].name
  }

  spec {
    replicas = var.simulation_mode ? 1 : 3

    selector {
      match_labels = {
        app = "l5-orchestrator"
      }
    }

    template {
      metadata {
        labels = {
          app = "l5-orchestrator"
        }
      }

      spec {
        container {
          image = "l5-orchestrator:latest"
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
  value = kubernetes_namespace.l5_namespace.metadata[0].name
}