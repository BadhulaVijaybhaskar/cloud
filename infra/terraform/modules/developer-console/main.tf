terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "atom-cloud"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "j2-dev-0"
}

resource "kubernetes_deployment" "developer_console_core" {
  metadata {
    name      = "developer-console-core"
    namespace = var.namespace
  }
  
  spec {
    replicas = 1
    
    selector {
      match_labels = {
        app = "developer-console-core"
      }
    }
    
    template {
      metadata {
        labels = {
          app = "developer-console-core"
        }
      }
      
      spec {
        container {
          image = "localhost:5000/atom-cloud/developer-console-core:${var.image_tag}"
          name  = "core"
          
          port {
            container_port = 8091
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "developer_console_core" {
  metadata {
    name      = "developer-console-core"
    namespace = var.namespace
  }
  
  spec {
    selector = {
      app = "developer-console-core"
    }
    
    port {
      port        = 8091
      target_port = 8091
    }
  }
}