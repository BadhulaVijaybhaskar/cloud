output "namespace" {
  value = kubernetes_namespace.k6.metadata[0].name
}