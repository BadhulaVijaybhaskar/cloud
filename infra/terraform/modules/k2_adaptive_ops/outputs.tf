output "namespace" {
  description = "K2 adaptive ops namespace"
  value       = kubernetes_namespace.k2_adaptive_ops.metadata[0].name
}

output "helm_release_name" {
  description = "K2 adaptive ops Helm release name"
  value       = helm_release.k2_adaptive_ops.name
}

output "helm_release_status" {
  description = "K2 adaptive ops Helm release status"
  value       = helm_release.k2_adaptive_ops.status
}

output "config_map_name" {
  description = "K2 configuration ConfigMap name"
  value       = kubernetes_config_map.k2_config.metadata[0].name
}

output "hpa_enabled" {
  description = "Whether HPA is enabled"
  value       = var.autoscale_enabled
}