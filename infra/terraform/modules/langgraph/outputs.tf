# LangGraph Terraform Module Outputs

output "namespace" {
  description = "Kubernetes namespace where LangGraph is deployed"
  value       = kubernetes_namespace.langgraph.metadata[0].name
}

output "service_endpoints" {
  description = "Service endpoints for LangGraph components"
  value = {
    core_service = "http://langgraph-core.${kubernetes_namespace.langgraph.metadata[0].name}.svc.cluster.local:8080"
    api_service  = "http://langgraph-api.${kubernetes_namespace.langgraph.metadata[0].name}.svc.cluster.local:8081"
  }
}

output "helm_release_name" {
  description = "Name of the Helm release"
  value       = helm_release.langgraph.name
}

output "helm_release_version" {
  description = "Version of the deployed Helm release"
  value       = helm_release.langgraph.version
}

output "config_map_name" {
  description = "Name of the ConfigMap containing LangGraph configuration"
  value       = kubernetes_config_map.langgraph_config.metadata[0].name
}

output "secret_name" {
  description = "Name of the Secret containing LangGraph credentials"
  value       = kubernetes_secret.langgraph_secrets.metadata[0].name
}

output "service_monitor_enabled" {
  description = "Whether ServiceMonitor is enabled for Prometheus"
  value       = var.monitoring_enabled
}

output "network_policy_enabled" {
  description = "Whether NetworkPolicy is enabled"
  value       = var.network_policy_enabled
}

output "service_mesh_enabled" {
  description = "Whether service mesh integration is enabled"
  value       = var.service_mesh_enabled
}

output "simulation_mode" {
  description = "Whether simulation mode is enabled"
  value       = var.simulation_mode
}