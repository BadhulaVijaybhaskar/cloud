# LangGraph Terraform Module

terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

# Namespace for LangGraph services
resource "kubernetes_namespace" "langgraph" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name"      = "langgraph"
      "app.kubernetes.io/component" = "graph-execution"
      "app.kubernetes.io/part-of"   = "atom-cloud"
    }
  }
}

# ConfigMap for LangGraph configuration
resource "kubernetes_config_map" "langgraph_config" {
  metadata {
    name      = "langgraph-config"
    namespace = kubernetes_namespace.langgraph.metadata[0].name
  }

  data = {
    "COMPONENT_NAME"    = "langgraph"
    "SIMULATION_MODE"   = var.simulation_mode
    "REDIS_URL"         = var.redis_url
    "POSTGRES_URL"      = var.postgres_url
    "SERVICE_MESH_ENABLED" = var.service_mesh_enabled
  }
}

# Secret for LangGraph credentials
resource "kubernetes_secret" "langgraph_secrets" {
  metadata {
    name      = "langgraph-secrets"
    namespace = kubernetes_namespace.langgraph.metadata[0].name
  }

  type = "Opaque"

  data = {
    "postgres-password" = base64encode(var.postgres_password)
    "redis-password"    = base64encode(var.redis_password)
    "jwt-secret"        = base64encode(var.jwt_secret)
  }
}

# Helm release for LangGraph
resource "helm_release" "langgraph" {
  name       = "langgraph"
  repository = var.helm_repository
  chart      = var.helm_chart_path
  namespace  = kubernetes_namespace.langgraph.metadata[0].name
  version    = var.helm_chart_version

  values = [
    templatefile("${path.module}/values.yaml.tpl", {
      namespace           = kubernetes_namespace.langgraph.metadata[0].name
      simulation_mode     = var.simulation_mode
      service_mesh_enabled = var.service_mesh_enabled
      image_tag          = var.image_tag
      replica_count      = var.replica_count
      postgres_url       = var.postgres_url
      redis_url          = var.redis_url
    })
  ]

  depends_on = [
    kubernetes_namespace.langgraph,
    kubernetes_config_map.langgraph_config,
    kubernetes_secret.langgraph_secrets
  ]
}

# Service Monitor for Prometheus
resource "kubernetes_manifest" "langgraph_service_monitor" {
  count = var.monitoring_enabled ? 1 : 0

  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "ServiceMonitor"
    metadata = {
      name      = "langgraph-metrics"
      namespace = kubernetes_namespace.langgraph.metadata[0].name
      labels = {
        "app.kubernetes.io/name" = "langgraph"
        "monitoring"             = "enabled"
      }
    }
    spec = {
      selector = {
        matchLabels = {
          "app.kubernetes.io/name" = "langgraph"
        }
      }
      endpoints = [
        {
          port     = "metrics"
          path     = "/metrics"
          interval = "30s"
        }
      ]
    }
  }
}

# Network Policy for LangGraph
resource "kubernetes_network_policy" "langgraph_network_policy" {
  count = var.network_policy_enabled ? 1 : 0

  metadata {
    name      = "langgraph-network-policy"
    namespace = kubernetes_namespace.langgraph.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        "app.kubernetes.io/name" = "langgraph"
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            "name" = "atom-cloud"
          }
        }
      }
      ports {
        protocol = "TCP"
        port     = "8080"
      }
    }

    egress {
      to {
        namespace_selector {
          match_labels = {
            "name" = "atom-cloud"
          }
        }
      }
    }
  }
}