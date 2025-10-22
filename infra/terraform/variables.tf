variable "database_url" {
  description = "PostgreSQL connection URL"
  type        = string
  sensitive   = true
}

variable "vault_addr" {
  description = "Vault server address"
  type        = string
  default     = "http://vault:8200"
}

variable "openai_api_key" {
  description = "OpenAI API key for embeddings"
  type        = string
  sensitive   = true
  default     = ""
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}