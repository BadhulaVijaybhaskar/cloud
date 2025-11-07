# L.5 Cognitive Federation Scaling Vault Policy
# P36 - Federated Scaling Safety

path "secret/data/l5/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/l5/*" {
  capabilities = ["list", "read", "delete"]
}

# Model signing keys
path "pki/l5/sign/model-cert" {
  capabilities = ["create", "update"]
}

# Federated rollout approvals
path "secret/data/l5/approvals/*" {
  capabilities = ["create", "read", "update"]
}

# Cross-region mTLS certificates
path "pki/l5/issue/federation-cert" {
  capabilities = ["create", "update"]
}