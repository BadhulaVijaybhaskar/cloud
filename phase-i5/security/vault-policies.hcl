# Vault policies for Phase I.5 CIN services

# Signal Gateway policy
path "secret/data/cin/signal-gateway/*" {
  capabilities = ["read"]
}

path "pki/issue/cin-services" {
  capabilities = ["create", "update"]
}

# FL Orchestrator policy  
path "secret/data/cin/fl-orchestrator/*" {
  capabilities = ["read"]
}

path "transit/encrypt/fl-models" {
  capabilities = ["create", "update"]
}

path "transit/decrypt/fl-models" {
  capabilities = ["create", "update"]
}

# Arbiter policy
path "secret/data/cin/arbiter/*" {
  capabilities = ["read"]
}

path "transit/sign/decisions" {
  capabilities = ["create", "update"]
}

# Consensus Bus policy
path "secret/data/cin/consensus-bus/*" {
  capabilities = ["read"]
}

# Model Store policy
path "secret/data/cin/model-store/*" {
  capabilities = ["read", "create", "update"]
}

path "transit/encrypt/model-artifacts" {
  capabilities = ["create", "update"]
}

# Audit Log policy
path "secret/data/cin/audit-log/*" {
  capabilities = ["read"]
}

path "transit/sign/audit-entries" {
  capabilities = ["create", "update"]
}

# Privacy Proxy policy
path "secret/data/cin/privacy-proxy/*" {
  capabilities = ["read"]
}

path "transit/encrypt/privacy-data" {
  capabilities = ["create", "update"]
}

# Admin policy for CIN management
path "secret/data/cin/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/kubernetes/role/cin-*" {
  capabilities = ["create", "read", "update", "delete"]
}