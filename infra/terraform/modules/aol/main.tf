terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

resource "kubernetes_namespace" "aol" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "aol"
      "phase" = "k1"
    }
  }
}

resource "helm_release" "aol" {
  name       = "aol"
  namespace  = kubernetes_namespace.aol.metadata[0].name
  chart      = var.helm_chart_path
  
  values = [
    templatefile("${path.module}/values.yaml.tpl", {
      simulation_mode = var.simulation_mode
      autonomous_mode = var.autonomous_mode
      image_registry  = var.image_registry
      image_tag      = var.image_tag
    })
  ]

  depends_on = [kubernetes_namespace.aol]
}

resource "kubernetes_config_map" "aol_config" {
  metadata {
    name      = "aol-config"
    namespace = kubernetes_namespace.aol.metadata[0].name
  }

  data = {
    "SIMULATION_MODE"  = var.simulation_mode
    "AUTONOMOUS_MODE"  = var.autonomous_mode
    "POLICY_ENFORCEMENT" = "true"
  }
}