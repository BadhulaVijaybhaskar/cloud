# Policy: l7_federated_continuum.hcl
# Grants read access to model registry path and write to audit logs (simulated)
path "secret/data/l7/*" {
  capabilities = ["read", "list"]
}
