# Production Vault Policy for ATOM Cloud Platform
# Phase J.5 - Production Cutover

# Database secrets
path "secret/data/database/*" {
  capabilities = ["read"]
}

# Service authentication
path "secret/data/services/*" {
  capabilities = ["read"]
}

# Partner federation secrets
path "secret/data/partners/*" {
  capabilities = ["read"]
}

# Billing and metering
path "secret/data/billing/*" {
  capabilities = ["read"]
}

# Monitoring credentials
path "secret/data/monitoring/*" {
  capabilities = ["read"]
}

# Certificate management
path "pki/issue/atom-cloud" {
  capabilities = ["create", "update"]
}

# Transit encryption
path "transit/encrypt/atom-cloud" {
  capabilities = ["update"]
}

path "transit/decrypt/atom-cloud" {
  capabilities = ["update"]
}

# Audit log access (read-only)
path "sys/audit" {
  capabilities = ["read"]
}

# Health check
path "sys/health" {
  capabilities = ["read"]
}