variable "namespace" {
  description = "Kubernetes namespace for K2 adaptive ops services"
  type        = string
  default     = "atom-k2"
}

variable "simulation_mode" {
  description = "Enable simulation mode for K2 services"
  type        = string
  default     = "true"
}

variable "autoscale_enabled" {
  description = "Enable autoscaling for K2 services"
  type        = bool
  default     = true
}

variable "ml_enabled" {
  description = "Enable ML features for predictive ops"
  type        = bool
  default     = true
}

variable "image_registry" {
  description = "Container image registry"
  type        = string
  default     = "registry.atomcloud.io"
}

variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "helm_chart_path" {
  description = "Path to K2 adaptive ops Helm chart"
  type        = string
  default     = "../../../helm/k2-adaptive-ops"
}

variable "replica_count" {
  description = "Default replica count for services"
  type        = number
  default     = 2
}