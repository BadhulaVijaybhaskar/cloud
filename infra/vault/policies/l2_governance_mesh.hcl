# Vault policy for L.2 Governance Mesh
path "secret/data/l2/*" {
  capabilities = ["read", "list"]
}

# Delegation tokens
path "secret/data/l2/delegation/*" {
  capabilities = ["create", "read", "update"]
}

# Billing ledger encryption keys
path "secret/data/l2/ledger/encryption" {
  capabilities = ["read"]
}

# Policy approval secrets
path "secret/data/l2/governance/approvals" {
  capabilities = ["create", "read", "list"]
}