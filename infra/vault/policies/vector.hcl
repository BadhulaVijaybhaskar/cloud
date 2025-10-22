path "secret/data/vector/*" {
  capabilities = ["read"]
}

path "secret/data/shared/*" {
  capabilities = ["read"]
}

path "database/creds/vector-role" {
  capabilities = ["read"]
}