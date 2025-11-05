output "namespace" {
  description = "AOL namespace"
  value       = kubernetes_namespace.aol.metadata[0].name
}

output "helm_release_name" {
  description = "AOL Helm release name"
  value       = helm_release.aol.name
}

output "helm_release_status" {
  description = "AOL Helm release status"
  value       = helm_release.aol.status
}

output "config_map_name" {
  description = "AOL configuration ConfigMap name"
  value       = kubernetes_config_map.aol_config.metadata[0].name
}