# ATOM Marketplace Terraform Module
terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  description = "Kubernetes namespace"
  type = string
  default = "atom-marketplace"
}

variable "simulation_mode" {
  description = "Enable simulation mode"
  type = bool
  default = true
}

variable "service_mesh_enabled" {
  description = "Enable service mesh"
  type = bool
  default = false
}

resource "kubernetes_namespace" "marketplace" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "atom-marketplace"
    }
  }
}

resource "kubernetes_config_map" "marketplace_config" {
  metadata {
    name = "marketplace-config"
    namespace = var.namespace
  }
  data = {
    SIMULATION_MODE = tostring(var.simulation_mode)
    MODEL_ARTIFACT_BUCKET = "atom-models-sim"
  }
}