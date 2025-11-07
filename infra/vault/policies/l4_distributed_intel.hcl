# Vault policy for L.4 Distributed Intelligence Federation
path "secret/data/l4/*" {
  capabilities = ["create","read","update","delete","list"]
}

# Model registry secrets
path "secret/data/l4/models/*" {
  capabilities = ["read","list"]
}

# Edge node authentication
path "secret/data/l4/edge/*" {
  capabilities = ["read"]
}