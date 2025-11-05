# P22 - Autonomous Remediation Safety Policy
# K.3 Self-Healing vault policy

path "secret/data/k3/*" {
  capabilities = ["read"]
}

path "secret/data/k3/healing/*" {
  capabilities = ["read", "update"]
}

# Allow reading incident patterns
path "secret/data/incidents/*" {
  capabilities = ["read"]
}

# Allow updating healing actions log
path "secret/data/healing/actions/*" {
  capabilities = ["create", "read", "update"]
}

# Restrict dangerous operations
path "secret/data/production/*" {
  capabilities = ["deny"]
}

# P22 Policy Rules:
# - Only one healing action per service per 15 min
# - Mandatory post-action verification  
# - Rollback on health regression
# - Incident log must include reason & duration