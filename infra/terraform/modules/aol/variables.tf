variable "namespace" {
  description = "Kubernetes namespace for AOL services"
  type        = string
  default     = "atom-auto"
}

variable "simulation_mode" {
  description = "Enable simulation mode for AOL"
  type        = string
  default     = "true"
}

variable "autonomous_mode" {
  description = "Enable autonomous mode for AOL"
  type        = string
  default     = "false"
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
  description = "Path to AOL Helm chart"
  type        = string
  default     = "../../../helm/aol"
}