# infra/vault/policies/k7_partner.hcl
# K.7 Partner Ecosystem Vault policy (simulation-safe)
# This policy file references existing P1-P27 hierarchy and adds partner-scoped rules.

path "secret/data/k7/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "kv/data/partners/*" {
  capabilities = ["read", "list"]
}

# Allow read-only access to public signing keys path for verification
path "kv/data/partners/keys/*" {
  capabilities = ["read", "list"]
}

# Admin operations (requires operator role)
path "secret/data/k7/admin/*" {
  capabilities = ["create","read","update","delete","list"]
}

# Note: In production, tighten these capabilities and scope to service accounts.