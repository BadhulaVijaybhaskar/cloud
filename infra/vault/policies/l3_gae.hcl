# Vault policy for L.3 Global Autonomy Exchange
path "secret/data/l3_gae/*" {
  capabilities = ["read", "create", "update", "list"]
}

# Cross-region mTLS certificates
path "secret/data/l3_gae/mtls/*" {
  capabilities = ["read"]
}

# Exchange audit keys
path "secret/data/l3_gae/audit/*" {
  capabilities = ["create", "read"]
}