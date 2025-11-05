# P23 - Knowledge Transfer Safety Policy
# K.4 Cognitive Optimization vault policy

path "secret/data/k4/*" {
  capabilities = ["read"]
}

path "secret/data/k4/experiences/*" {
  capabilities = ["read", "create", "update"]
}

path "secret/data/k4/transfers/*" {
  capabilities = ["read", "create", "update"]
}

# Allow reading anonymized patterns
path "secret/data/patterns/*" {
  capabilities = ["read"]
}

# Allow updating optimization results
path "secret/data/optimizations/*" {
  capabilities = ["create", "read", "update"]
}

# Restrict access to raw tenant data
path "secret/data/tenants/*" {
  capabilities = ["deny"]
}

# P23 Policy Rules:
# - All transfers must be anonymized
# - Require explicit approval for live transfers
# - Maintain complete audit trail
# - Include origin proof for all experiences