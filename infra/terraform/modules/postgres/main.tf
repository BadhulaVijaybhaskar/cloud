resource "kubernetes_secret" "postgres" {
  metadata {
    name      = "postgres-secret"
    namespace = "default"
  }
  data = {
    url      = var.database_url
    username = var.postgres_user
    password = var.postgres_password
    database = var.postgres_db
  }
}

output "db_url" {
  value = var.database_url
}