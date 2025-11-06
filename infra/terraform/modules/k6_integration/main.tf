// K.6 Integration plane terraform module (stub)
terraform {
  required_version = ">= 1.0"
}

provider "kubernetes" {
  # configured by CI/operator
}

resource "kubernetes_namespace" "k6" {
  metadata { name = var.namespace }
}

# Placeholder: create configmaps / service accounts for connectors and edge orchestrator

variable "namespace" {
  type = string
  default = "atom-k6"
}