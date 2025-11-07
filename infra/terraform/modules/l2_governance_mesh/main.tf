terraform {
  required_version = ">= 1.0"
}

provider "kubernetes" {
  # configured by operator
}

resource "kubernetes_namespace" "l2_ns" {
  metadata {
    name = var.namespace
    labels = { 
      app = "l2-governance-mesh"
      phase = "L.2"
    }
  }
}

output "namespace" { 
  value = kubernetes_namespace.l2_ns.metadata[0].name 
}