variable "namespace" {
  description = "Kubernetes namespace for M.1 services"
  type        = string
  default     = "atom-m1"
}

variable "simulation_mode" {
  description = "Enable simulation mode"
  type        = bool
  default     = true
}

variable "docker_registry" {
  description = "Docker registry for images"
  type        = string
  default     = "localhost:5000"
}