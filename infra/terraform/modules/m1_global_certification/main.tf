terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

resource "kubernetes_namespace" "m1" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "m1-global-certification"
      "atom.cloud/phase" = "m1"
    }
  }
}

resource "kubernetes_deployment" "gca_core" {
  metadata {
    name      = "m1-gca-core"
    namespace = kubernetes_namespace.m1.metadata[0].name
  }
  
  spec {
    replicas = var.simulation_mode ? 1 : 3
    
    selector {
      match_labels = {
        app = "m1-gca-core"
      }
    }
    
    template {
      metadata {
        labels = {
          app = "m1-gca-core"
        }
      }
      
      spec {
        container {
          name  = "gca-core"
          image = "${var.docker_registry}/m1-gca-core:latest"
          
          port {
            container_port = 9200
          }
          
          env {
            name  = "SIMULATION_MODE"
            value = var.simulation_mode
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "gca_core" {
  metadata {
    name      = "m1-gca-core"
    namespace = kubernetes_namespace.m1.metadata[0].name
  }
  
  spec {
    selector = {
      app = "m1-gca-core"
    }
    
    port {
      port        = 9200
      target_port = 9200
    }
  }
}