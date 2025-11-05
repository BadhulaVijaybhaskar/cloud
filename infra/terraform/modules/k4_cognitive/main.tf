variable "namespace" {
  type    = string
  default = "atom-k4"
}

variable "simulation_mode" {
  type    = bool
  default = true
}

variable "approve_transfer" {
  type    = bool
  default = false
}

resource "kubernetes_namespace" "k4_namespace" {
  metadata {
    name = var.namespace
    labels = {
      "app" = "k4-cognitive"
      "phase" = "k4"
    }
  }
}

resource "kubernetes_service_account" "k4_service_account" {
  metadata {
    name      = "k4-service-account"
    namespace = kubernetes_namespace.k4_namespace.metadata[0].name
  }
}

resource "kubernetes_config_map" "k4_config" {
  metadata {
    name      = "k4-config"
    namespace = kubernetes_namespace.k4_namespace.metadata[0].name
  }

  data = {
    SIMULATION_MODE = var.simulation_mode
    APPROVE_TRANSFER = var.approve_transfer
    PHASE = "K.4"
    GOVERNANCE_POLICY = "P23"
  }
}

resource "helm_release" "k4_cognitive" {
  name       = "k4-cognitive"
  chart      = "../../helm/k4-cognitive"
  namespace  = kubernetes_namespace.k4_namespace.metadata[0].name

  set {
    name  = "simulationMode"
    value = var.simulation_mode
  }

  set {
    name  = "approveTransfer"
    value = var.approve_transfer
  }
}