# Vault policy for K.8 billing usage - simulation safe
path "secret/data/k8/billing/*" {
  capabilities = ["read","list"]
}

path "sys/policies/acl/k8_billing" {
  capabilities = ["read","list"]
}