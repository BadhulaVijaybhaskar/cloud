# AOL Vault Policy for Autonomous Runtime
# Phase K.1 - Autonomous Runtime Activation

# AOL service secrets
path "secret/data/aol/*" {
  capabilities = ["read"]
}

# Kubernetes service account tokens
path "auth/kubernetes/role/aol-controller" {
  capabilities = ["read"]
}

path "auth/kubernetes/role/aol-executor" {
  capabilities = ["read"]
}

# Policy engine configuration
path "secret/data/policies/*" {
  capabilities = ["read"]
}

# Monitoring and audit
path "secret/data/monitoring/aol" {
  capabilities = ["read"]
}

# Transit encryption for sensitive decisions
path "transit/encrypt/aol-decisions" {
  capabilities = ["update"]
}

path "transit/decrypt/aol-decisions" {
  capabilities = ["update"]
}