# M.1 Global Certification Vault Policy
# Enforces P43-P46 governance policies

# GCA Core signing permissions
path "secret/data/m1/gca/signing_key" {
  capabilities = ["read"]
}

# Cross-domain policy access
path "secret/data/m1/policies/*" {
  capabilities = ["read", "list"]
}

# Audit logging
path "secret/data/m1/audit/*" {
  capabilities = ["create", "read", "list"]
}

# Metrics collection
path "secret/data/m1/metrics/*" {
  capabilities = ["create", "read", "update", "list"]
}

# P43: Multi-role approval for key operations
path "secret/data/m1/gca/master_key" {
  capabilities = ["read"]
  required_parameters = ["approver_1", "approver_2"]
}

# P44: Cross-domain policy validation
path "secret/data/m1/cross_domain/*" {
  capabilities = ["read"]
  allowed_parameters = {
    "domain" = ["federation-a", "federation-b", "federation-c"]
  }
}

# P45: Audit trail enforcement
path "audit/*" {
  capabilities = ["create"]
  required_parameters = ["action", "timestamp", "user"]
}

# P46: Compliance reporting
path "secret/data/m1/compliance/*" {
  capabilities = ["read", "list"]
}