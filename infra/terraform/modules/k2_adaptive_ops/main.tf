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

resource "kubernetes_namespace" "k2_adaptive_ops" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "k2-adaptive-ops"
      "phase" = "k2"
    }
  }
}

resource "kubernetes_config_map" "k2_config" {
  metadata {
    name      = "k2-adaptive-ops-config"
    namespace = kubernetes_namespace.k2_adaptive_ops.metadata[0].name
  }

  data = {
    "SIMULATION_MODE"  = var.simulation_mode
    "AUTOSCALE_ENABLED" = var.autoscale_enabled
    "ML_ENABLED" = var.ml_enabled
    "TRAINING_INTERVAL_HOURS" = "12"
  }
}

resource "helm_release" "k2_adaptive_ops" {
  name       = "k2-adaptive-ops"
  namespace  = kubernetes_namespace.k2_adaptive_ops.metadata[0].name
  chart      = var.helm_chart_path
  
  values = [
    templatefile("${path.module}/values.yaml.tpl", {
      simulation_mode = var.simulation_mode
      autoscale_enabled = var.autoscale_enabled
      ml_enabled = var.ml_enabled
      image_registry = var.image_registry
      image_tag = var.image_tag
    })
  ]

  depends_on = [kubernetes_namespace.k2_adaptive_ops]
}

resource "kubernetes_horizontal_pod_autoscaler" "predictive_engine_hpa" {
  count = var.autoscale_enabled ? 1 : 0
  
  metadata {
    name      = "predictive-ops-engine-hpa"
    namespace = kubernetes_namespace.k2_adaptive_ops.metadata[0].name
  }

  spec {
    max_replicas = 10
    min_replicas = 2

    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = "predictive-ops-engine"
    }

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }
  }
}