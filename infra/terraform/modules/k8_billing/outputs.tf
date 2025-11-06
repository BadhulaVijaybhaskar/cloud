output "namespace" {
  value = kubernetes_namespace.k8_namespace.metadata[0].name
}