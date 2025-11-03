# LangGraph Terraform Module Variables

variable "namespace" {
  description = "Kubernetes namespace for LangGraph services"
  type        = string
  default     = "langgraph"
}

variable "simulation_mode" {
  description = "Enable simulation mode for development"
  type        = string
  default     = "true"
}

variable "service_mesh_enabled" {
  description = "Enable service mesh integration"
  type        = string
  default     = "false"
}

variable "image_tag" {
  description = "Docker image tag for LangGraph services"
  type        = string
  default     = "1.0.0"
}

variable "replica_count" {
  description = "Number of replicas for LangGraph services"
  type        = number
  default     = 2
}

variable "postgres_url" {
  description = "PostgreSQL connection URL"
  type        = string
  default     = "postgresql://langgraph:changeme@postgresql:5432/langgraph"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "changeme"
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
  default     = "redis://redis:6379/0"
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  default     = "changeme"
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT secret for authentication"
  type        = string
  default     = "dev-secret-key"
  sensitive   = true
}

variable "helm_repository" {
  description = "Helm repository URL"
  type        = string
  default     = ""
}

variable "helm_chart_path" {
  description = "Path to Helm chart"
  type        = string
  default     = "./helm/langgraph"
}

variable "helm_chart_version" {
  description = "Helm chart version"
  type        = string
  default     = "1.0.0"
}

variable "monitoring_enabled" {
  description = "Enable Prometheus monitoring"
  type        = bool
  default     = true
}

variable "network_policy_enabled" {
  description = "Enable Kubernetes network policies"
  type        = bool
  default     = false
}

variable "resource_limits" {
  description = "Resource limits for LangGraph services"
  type = object({
    cpu    = string
    memory = string
  })
  default = {
    cpu    = "1000m"
    memory = "1Gi"
  }
}

variable "resource_requests" {
  description = "Resource requests for LangGraph services"
  type = object({
    cpu    = string
    memory = string
  })
  default = {
    cpu    = "500m"
    memory = "512Mi"
  }
}

variable "autoscaling_enabled" {
  description = "Enable horizontal pod autoscaling"
  type        = bool
  default     = true
}

variable "autoscaling_min_replicas" {
  description = "Minimum number of replicas for autoscaling"
  type        = number
  default     = 2
}

variable "autoscaling_max_replicas" {
  description = "Maximum number of replicas for autoscaling"
  type        = number
  default     = 10
}

variable "autoscaling_target_cpu" {
  description = "Target CPU utilization percentage for autoscaling"
  type        = number
  default     = 70
}