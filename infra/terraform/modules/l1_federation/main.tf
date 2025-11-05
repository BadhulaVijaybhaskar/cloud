terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  description = "Kubernetes namespace for L1 federation services"
  type        = string
  default     = "atom-federation"
}

variable "simulation_mode" {
  description = "Enable simulation mode"
  type        = bool
  default     = true
}

variable "approve_federation" {
  description = "Enable live federation actions"
  type        = bool
  default     = false
}

resource "kubernetes_namespace" "l1_federation" {
  metadata {
    name = var.namespace
    labels = {
      "phase" = "l1"
      "simulation-mode" = tostring(var.simulation_mode)
      "federation-enabled" = tostring(var.approve_federation)
    }
  }
}

resource "kubernetes_config_map" "l1_config" {
  metadata {
    name      = "l1-federation-config"
    namespace = kubernetes_namespace.l1_federation.metadata[0].name
  }

  data = {
    SIMULATION_MODE = tostring(var.simulation_mode)
    APPROVE_FEDERATION = tostring(var.approve_federation)
    FEDERATION_ORCHESTRATOR_URL = "http://federation-orchestrator:8900"
    FEDERATION_GATEWAY_URL = "http://federation-gateway:8901"
    FEDERATION_METADATA_URL = "http://federation-metadata:8902"
    FEDERATION_POLICY_BROKER_URL = "http://federation-policy-broker:8903"
    FEDERATION_MIRROR_AGENT_URL = "http://federation-mirror-agent:8904"
    FEDERATION_HEARTBEAT_SEC = "30"
    METADATA_SYNC_INTERVAL_SEC = "300"
    OPT_IN_EXPIRY_DAYS = "365"
  }
}

output "namespace" {
  value = kubernetes_namespace.l1_federation.metadata[0].name
}

output "config_map" {
  value = kubernetes_config_map.l1_config.metadata[0].name
}