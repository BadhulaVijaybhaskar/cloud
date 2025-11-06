# infra/vault/policies/k2_adaptive_ops.hcl
# K.2 Vault policy - restrict model keys and rotation

# K2 adaptive ops secrets
path "secret/data/k2/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Model artifacts and ML secrets
path "secret/data/models/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Predictive ops engine secrets
path "secret/data/predictive-ops/*" {
  capabilities = ["create", "read", "update", "list"]
}

# Training worker secrets
path "secret/data/training/*" {
  capabilities = ["create", "read", "update", "list"]
}

# Read access to system policies
path "sys/policies/acl" {
  capabilities = ["read", "list"]
}

# Auth method access for service authentication
path "auth/kubernetes/role/k2-adaptive-ops" {
  capabilities = ["read"]
}

# P21 - Predictive Execution Safety Policy
# All forecast-driven decisions must be logged and approved
path "secret/data/k2/decisions/*" {
  capabilities = ["create", "read", "list"]
}

path "secret/data/k2/audit/*" {
  capabilities = ["create", "read", "list"]
}