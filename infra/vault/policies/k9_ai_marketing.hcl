# Vault policy for K.9 AI Marketing Agent
path "secret/data/k9/*" {
  capabilities = ["read","list"]
}

# Marketing safety: only authorized roles may write live outbound credentials
path "secret/data/k9/outbound_creds" {
  capabilities = ["deny"]
}

# Operators may approve deployment via special admin policy (separate)