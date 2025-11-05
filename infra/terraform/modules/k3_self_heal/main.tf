variable "namespace" {
  type    = string
  default = "atom-k3"
}

variable "simulation_mode" {
  type    = bool
  default = true
}

resource "kubernetes_namespace" "k3_namespace" {
  metadata {
    name = var.namespace
    labels = {
      "app" = "k3-self-heal"
      "phase" = "k3"
    }
  }
}

resource "kubernetes_service_account" "k3_service_account" {
  metadata {
    name      = "k3-service-account"
    namespace = kubernetes_namespace.k3_namespace.metadata[0].name
  }
}

resource "kubernetes_config_map" "k3_config" {
  metadata {
    name      = "k3-config"
    namespace = kubernetes_namespace.k3_namespace.metadata[0].name
  }

  data = {
    SIMULATION_MODE = var.simulation_mode
    PHASE = "K.3"
    GOVERNANCE_ENFORCE = "true"
  }
}

resource "helm_release" "k3_self_heal" {
  name       = "k3-self-heal"
  chart      = "../../helm/k3-self-heal"
  namespace  = kubernetes_namespace.k3_namespace.metadata[0].name

  set {
    name  = "simulationMode"
    value = var.simulation_mode
  }

  set {
    name  = "autonomous.enabled"
    value = !var.simulation_mode
  }
}