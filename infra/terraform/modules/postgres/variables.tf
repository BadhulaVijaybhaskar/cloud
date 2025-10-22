variable "database_url" {
  type = string
}
variable "postgres_user" {
  type = string
  default = "postgres"
}
variable "postgres_password" {
  type = string
  sensitive = true
}
variable "postgres_db" {
  type = string
  default = "naksha"
}