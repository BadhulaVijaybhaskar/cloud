# K.5 Full Autonomy Vault Policy (P24)
# Governs meta-learning, explainability, and autonomous proposal management

path "secret/data/k5/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/data/meta-learning/*" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/explainability/*" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/governance/policies/*" {
  capabilities = ["read"]
}

# Audit trail access (read-only for compliance)
path "secret/data/audit/k5/*" {
  capabilities = ["read", "list"]
}

# Simulation mode secrets
path "secret/data/simulation/k5/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Meta-proposal approval gates
path "secret/data/approvals/meta/*" {
  capabilities = ["read"]
}