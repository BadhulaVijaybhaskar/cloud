# BYOC Security Policy

## Overview
Security requirements and implementation for NeuralOps BYOC (Bring Your Own Cluster) Connector.

## Authentication & Authorization

### Vault Integration
- **Requirement:** All BYOC agents must authenticate via Vault AppRole
- **Implementation:** Agent retrieves JWT token using role_id/secret_id
- **Token Rotation:** Automatic token renewal every 24 hours
- **Fallback:** Simulation mode for development environments

### Cluster Registration
- **Requirement:** Valid Vault token required for cluster registration
- **Validation:** Control plane verifies token before accepting registration
- **Metadata:** Cluster ID, hostname, labels, and capabilities tracked

## Execution Security

### Cosign Verification
- **Requirement:** All WPK payloads must be cosign-signed
- **Implementation:** Agent verifies signature before execution
- **Key Management:** Public keys distributed via Vault secrets
- **Rejection:** Invalid signatures result in execution denial

### Kubernetes RBAC
- **Service Account:** Non-root service account with minimal permissions
- **Capabilities:** Only required Kubernetes API access granted
- **Network Policy:** Restricted network access to control plane only

## Data Protection

### Metrics Security
- **Encryption:** All metrics transmitted over HTTPS/TLS
- **Sanitization:** PII automatically redacted from metrics
- **Retention:** Local metrics cached for max 1 hour

### Audit Logging
- **Requirement:** All executions logged with SHA-256 integrity
- **Storage:** Local audit logs with daily S3 upload
- **Immutability:** Audit entries cannot be modified after creation
- **Retention:** 90-day retention policy for audit logs

## Network Security

### TLS Requirements
- **Control Plane:** All communication over HTTPS with valid certificates
- **Prometheus:** Secure metrics collection with authentication
- **Vault:** TLS-encrypted secret retrieval

### Firewall Rules
- **Outbound:** Only control plane and Vault endpoints allowed
- **Inbound:** Health check endpoint only (port 8005)
- **Internal:** Kubernetes API access for execution only

## Operational Security

### Safety Defaults
- **Mode:** Manual approval required by default
- **Auto-Execution:** Only for pre-approved, low-risk playbooks
- **Risk Assessment:** Dry-run validation before execution
- **Emergency Stop:** Immediate execution halt capability

### Monitoring & Alerting
- **Health Checks:** Continuous agent health monitoring
- **Failed Auth:** Alert on authentication failures
- **Execution Errors:** Alert on WPK execution failures
- **Network Issues:** Alert on control plane connectivity loss

## Compliance Requirements

### Data Residency
- **Metrics:** Processed locally, minimal data transmission
- **Audit Logs:** Stored in customer-controlled S3 bucket
- **Secrets:** Retrieved from customer Vault instance

### Access Control
- **Principle of Least Privilege:** Minimal required permissions only
- **Role Separation:** Distinct roles for registration, metrics, execution
- **Audit Trail:** Complete access logging for compliance

## Implementation Checklist

### Deployment Security
- ✅ Non-root container execution
- ✅ Read-only root filesystem
- ✅ Security context with dropped capabilities
- ✅ Resource limits and requests defined
- ✅ Network policies applied

### Runtime Security
- ✅ Vault token validation
- ✅ Cosign signature verification
- ✅ TLS certificate validation
- ✅ Audit logging with integrity hashes
- ✅ Error handling without information disclosure

### Operational Security
- ✅ Health monitoring endpoints
- ✅ Graceful degradation on failures
- ✅ Secure secret management
- ✅ Compliance-ready audit trails
- ✅ Emergency stop procedures

## Security Incident Response

### Detection
- Monitor for authentication failures
- Track execution anomalies
- Alert on network connectivity issues
- Log all security-relevant events

### Response
1. **Immediate:** Isolate affected agent
2. **Assessment:** Determine scope and impact
3. **Containment:** Revoke compromised credentials
4. **Recovery:** Deploy clean agent instance
5. **Lessons Learned:** Update security policies

## Regular Security Reviews

### Monthly
- Review audit logs for anomalies
- Validate certificate expiration dates
- Check for security updates

### Quarterly
- Penetration testing of agent endpoints
- Security policy review and updates
- Compliance audit preparation

### Annually
- Full security architecture review
- Third-party security assessment
- Disaster recovery testing