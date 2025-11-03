path "secret/data/developer-console/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/developer-console/*" {
  capabilities = ["list"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}