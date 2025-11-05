# L.1 Federation Vault Policy (P25-P27)
# Governs federated autonomy, cross-region actions, and data sovereignty

# Federation secrets access
path "secret/data/l1/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/data/federation/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Cross-region delegation tokens (dynamic secrets)
path "secret/data/delegation/*" {
  capabilities = ["create", "read", "update"]
}

# Node registration and metadata
path "secret/data/nodes/*" {
  capabilities = ["create", "read", "update", "list"]
}

# Opt-in records (immutable after creation)
path "secret/data/opt-in/*" {
  capabilities = ["create", "read", "list"]
}

# Policy validation results
path "secret/data/policy-validations/*" {
  capabilities = ["create", "read", "list"]
}

# Audit trail access (read-only for compliance)
path "secret/data/audit/l1/*" {
  capabilities = ["read", "list"]
}

# Simulation mode secrets
path "secret/data/simulation/l1/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Federation approval gates
path "secret/data/approvals/federation/*" {
  capabilities = ["read"]
}