terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  description = "Kubernetes namespace for K5 services"
  type        = string
  default     = "k5-full-autonomy"
}

variable "simulation_mode" {
  description = "Enable simulation mode"
  type        = bool
  default     = true
}

variable "approve_meta" {
  description = "Enable meta-proposal application"
  type        = bool
  default     = false
}

resource "kubernetes_namespace" "k5" {
  metadata {
    name = var.namespace
    labels = {
      "phase" = "k5"
      "simulation-mode" = tostring(var.simulation_mode)
    }
  }
}

resource "kubernetes_config_map" "k5_config" {
  metadata {
    name      = "k5-config"
    namespace = kubernetes_namespace.k5.metadata[0].name
  }

  data = {
    SIMULATION_MODE = tostring(var.simulation_mode)
    APPROVE_META    = tostring(var.approve_meta)
    META_LEARNER_URL = "http://meta-learner:8800"
    EXPLAINABILITY_URL = "http://explainability-engine:8801"
    POLICY_REFINER_URL = "http://policy-refiner:8802"
    AUDITOR_URL = "http://autonomy-auditor:8803"
    SIMULATOR_URL = "http://simulator-proxy:8804"
  }
}

output "namespace" {
  value = kubernetes_namespace.k5.metadata[0].name
}

output "config_map" {
  value = kubernetes_config_map.k5_config.metadata[0].name
}