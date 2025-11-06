terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  type    = string
  default = "atom-k8"
}

# Example: create namespace (k8s provider must be configured by operator)
resource "kubernetes_namespace" "k8_namespace" {
  metadata {
    name = var.namespace
    labels = {
      phase = "k8-billing"
    }
  }
}

output "namespace" {
  value = kubernetes_namespace.k8_namespace.metadata[0].name
}