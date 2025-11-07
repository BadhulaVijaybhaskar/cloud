# L.6 Cognitive Resilience Vault Policy
# P37 - Resilience Safety enforcement
# P38 - Cross-region TTL constraints

path "secret/data/l6/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/l6/*" {
  capabilities = ["list", "read", "delete"]
}

# P37: Resilience Safety - action approval tokens
path "secret/data/l6/approvals/*" {
  capabilities = ["create", "read", "update"]
}

# P38: Cross-region action TTL tokens
path "secret/data/l6/ttl/*" {
  capabilities = ["create", "read", "update"]
}

# Audit trail access
path "secret/data/l6/audit/*" {
  capabilities = ["create", "read", "list"]
}