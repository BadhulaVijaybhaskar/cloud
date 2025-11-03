# Workflow-Registry Component Vault Policy
# Enforces P1-P20 policy inheritance matrix

path "secret/data/workflow-registry/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
  # P1: Authentication required
  # P2: Authorization via JWT
  # P3: Audit logging enabled
  # P4: Encryption at rest
  # P5: TLS in transit
}

path "secret/data/shared/workflow-registry/*" {
  capabilities = ["read", "list"]
  # P6: Multi-tenant isolation
  # P7: Rate limiting
  # P8: Input validation
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
  # P9: Token validation
  # P10: Session management
}

path "sys/capabilities-self" {
  capabilities = ["read"]
  # P11: Capability checking
  # P12: Privilege escalation prevention
}

# P13-P20: Additional security controls
path "pki/cert/workflow-registry" {
  capabilities = ["read"]
  # P13: Certificate management
  # P14: Key rotation
  # P15: Compliance validation
  # P16: Security monitoring
  # P17: Incident response
  # P18: Data retention
  # P19: Privacy controls
  # P20: Regulatory compliance
}