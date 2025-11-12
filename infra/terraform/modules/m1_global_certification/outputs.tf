output "namespace" {
  description = "The namespace where M.1 services are deployed"
  value       = kubernetes_namespace.m1.metadata[0].name
}

output "gca_core_service" {
  description = "GCA Core service endpoint"
  value       = "${kubernetes_service.gca_core.metadata[0].name}.${kubernetes_namespace.m1.metadata[0].name}.svc.cluster.local:9200"
}