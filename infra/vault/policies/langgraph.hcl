path "secret/data/langgraph/*" {
  capabilities = ["read"]
}

path "secret/data/shared/*" {
  capabilities = ["read"]
}

path "database/creds/langgraph-role" {
  capabilities = ["read"]
}