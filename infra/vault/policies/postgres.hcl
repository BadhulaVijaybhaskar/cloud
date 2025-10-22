path "database/config/*" {
  capabilities = ["read"]
}

path "database/creds/*" {
  capabilities = ["read"]
}

path "secret/data/postgres/*" {
  capabilities = ["read", "create", "update"]
}