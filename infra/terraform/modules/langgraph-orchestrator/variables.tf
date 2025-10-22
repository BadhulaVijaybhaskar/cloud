variable "env" {
  description = "Environment variables for LangGraph service"
  type = object({
    DATABASE_URL  = string
    VECTOR_DB_URL = string
    VAULT_ADDR    = string
  })
}