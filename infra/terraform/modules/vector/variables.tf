variable "milvus_host" {
  type = string
  default = "milvus"
}
variable "openai_api_key" {
  type = string
  sensitive = true
}