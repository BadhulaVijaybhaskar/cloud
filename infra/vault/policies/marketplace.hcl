# ATOM Marketplace Vault Policy
# Secrets access for marketplace services

# Marketplace core service secrets
path "secret/data/marketplace/core/*" {
  capabilities = ["read"]
}

# Model registry database credentials
path "secret/data/marketplace/model-registry/db" {
  capabilities = ["read"]
}

# Agent registry secrets
path "secret/data/marketplace/agent-registry/*" {
  capabilities = ["read"]
}

# S3 bucket credentials for artifact storage
path "secret/data/marketplace/s3/*" {
  capabilities = ["read"]
}

# Billing service integration tokens
path "secret/data/marketplace/billing/*" {
  capabilities = ["read"]
}

# Cosign signing keys for package verification
path "secret/data/marketplace/cosign/*" {
  capabilities = ["read"]
}

# Marketplace worker service secrets
path "secret/data/marketplace/worker/*" {
  capabilities = ["read"]
}