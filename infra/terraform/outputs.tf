output "langgraph_endpoint" {
  description = "LangGraph service endpoint"
  value       = "http://langgraph:8080"
}

output "vector_endpoint" {
  description = "Vector service endpoint"
  value       = "http://vector:8081"
}

output "vault_addr" {
  description = "Vault server address"
  value       = var.vault_addr
}

output "prometheus_endpoint" {
  description = "Prometheus server endpoint"
  value       = "http://prometheus:9090"
}

output "grafana_endpoint" {
  description = "Grafana dashboard endpoint"
  value       = "http://grafana:3000"
}