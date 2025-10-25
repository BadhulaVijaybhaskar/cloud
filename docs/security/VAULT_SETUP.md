# HashiCorp Vault Integration Guide

## Overview

ATOM integrates with HashiCorp Vault for secure secret management, including cosign keys, database credentials, and API tokens. This guide covers setup, configuration, and usage.

## Prerequisites

- HashiCorp Vault server (v1.12+)
- Vault CLI installed
- Admin access to Vault server
- Kubernetes cluster (for Vault Agent/CSI integration)

## Vault Server Setup

### 1. Enable KV Secrets Engine

```bash
# Enable KV v2 secrets engine
vault secrets enable -path=secret kv-v2

# Verify
vault secrets list
```

### 2. Create ATOM Policies

```bash
# Create policy for ATOM services
vault policy write atom-policy - <<EOF
# Read ATOM secrets
path "secret/data/atom/*" {
  capabilities = ["read"]
}

# Allow token self-lookup
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
EOF
```

### 3. Configure AppRole Authentication

```bash
# Enable AppRole auth method
vault auth enable approle

# Create ATOM role
vault write auth/approle/role/atom \
    token_policies="atom-policy" \
    token_ttl=1h \
    token_max_ttl=4h \
    bind_secret_id=true

# Get role ID
vault read auth/approle/role/atom/role-id

# Generate secret ID
vault write -f auth/approle/role/atom/secret-id
```

## Secret Storage

### 1. Store Cosign Keys

```bash
# Generate cosign keys (if not already done)
cosign generate-key-pair

# Store public key in Vault
vault kv put secret/atom/cosign \
    public_key=@cosign.pub \
    private_key=@cosign.key

# Verify
vault kv get secret/atom/cosign
```

### 2. Store Database Credentials

```bash
# Store PostgreSQL DSN
vault kv put secret/atom/database \
    dsn="postgresql://user:password@localhost:5432/atom_db"

# For production, use separate fields
vault kv put secret/atom/database \
    host="postgres.example.com" \
    port="5432" \
    database="atom_prod" \
    username="atom_user" \
    password="secure_password"
```

### 3. Store S3 Credentials

```bash
# Store S3/MinIO credentials
vault kv put secret/atom/s3 \
    access_key="AKIAIOSFODNN7EXAMPLE" \
    secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
    bucket="atom-storage" \
    endpoint="https://s3.amazonaws.com"
```

### 4. Store API Credentials

```bash
# Prometheus credentials
vault kv put secret/atom/api/prometheus \
    url="https://prometheus.example.com" \
    username="atom" \
    password="prometheus_password"

# Grafana credentials
vault kv put secret/atom/api/grafana \
    url="https://grafana.example.com" \
    token="eyJrIjoiT0tTcG1pUlY2RnVKZTFVaDFsNFZXdE9ZWmNrMkZYbk"
```

## Kubernetes Integration

### 1. Vault Agent Sidecar

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-registry
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "atom"
        vault.hashicorp.com/agent-inject-secret-cosign: "secret/atom/cosign"
        vault.hashicorp.com/agent-inject-template-cosign: |
          {{- with secret "secret/atom/cosign" -}}
          export COSIGN_PUBLIC_KEY="{{ .Data.data.public_key }}"
          {{- end }}
    spec:
      serviceAccountName: atom-vault-sa
      containers:
      - name: registry
        image: atom/workflow-registry:latest
        command: ["/bin/sh"]
        args: ["-c", "source /vault/secrets/cosign && python main.py"]
```

### 2. Vault CSI Driver

```yaml
apiVersion: v1
kind: SecretProviderClass
metadata:
  name: atom-secrets
spec:
  provider: vault
  parameters:
    vaultAddress: "https://vault.example.com:8200"
    roleName: "atom"
    objects: |
      - objectName: "cosign-public-key"
        secretPath: "secret/atom/cosign"
        secretKey: "public_key"
      - objectName: "database-dsn"
        secretPath: "secret/atom/database"
        secretKey: "dsn"
```

### 3. Service Account Setup

```bash
# Create Kubernetes service account
kubectl create serviceaccount atom-vault-sa

# Create Vault Kubernetes auth role
vault write auth/kubernetes/role/atom \
    bound_service_account_names=atom-vault-sa \
    bound_service_account_namespaces=default \
    policies=atom-policy \
    ttl=24h
```

## Application Configuration

### 1. Environment Variables

```bash
# Vault server configuration
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_NAMESPACE="atom"  # For Vault Enterprise

# AppRole authentication
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"

# Alternative: Direct token (not recommended for production)
export VAULT_TOKEN="your-vault-token"
```

### 2. Helm Values

```yaml
# infra/helm/values/vault-values.yaml
vault:
  enabled: true
  address: "https://vault.example.com:8200"
  namespace: "atom"
  
  # AppRole configuration
  auth:
    method: "approle"
    roleId: "your-role-id"
    secretId: "your-secret-id"
  
  # Secret paths
  secrets:
    cosign: "secret/atom/cosign"
    database: "secret/atom/database"
    s3: "secret/atom/s3"

# Service configuration
services:
  workflowRegistry:
    vault:
      enabled: true
      secretPath: "secret/atom/cosign"
  
  runtimeAgent:
    vault:
      enabled: true
      secretPath: "secret/atom/kubernetes"
```

## Usage Examples

### 1. Python Application

```python
from services.workflow_registry.secrets import get_cosign_public_key, get_database_dsn

# Get secrets with Vault fallback
cosign_key = get_cosign_public_key()
db_dsn = get_database_dsn()

if cosign_key:
    print("Cosign key loaded from Vault")
else:
    print("Using fallback configuration")
```

### 2. CLI Usage

```bash
# Test Vault connectivity
vault status

# Read ATOM secrets
vault kv get secret/atom/cosign
vault kv get secret/atom/database

# Test AppRole authentication
vault write auth/approle/login \
    role_id="$VAULT_ROLE_ID" \
    secret_id="$VAULT_SECRET_ID"
```

## Security Best Practices

### 1. Secret Rotation

```bash
# Rotate cosign keys
cosign generate-key-pair
vault kv put secret/atom/cosign \
    public_key=@cosign.pub \
    private_key=@cosign.key

# Rotate database password
vault kv patch secret/atom/database \
    password="new_secure_password"
```

### 2. Access Control

- Use least-privilege policies
- Implement secret versioning
- Enable audit logging
- Regular access reviews

### 3. Monitoring

```bash
# Enable audit logging
vault audit enable file file_path=/vault/logs/audit.log

# Monitor secret access
vault read sys/internal/counters/requests
```

## Troubleshooting

### Common Issues

1. **"Permission denied" errors**
   ```bash
   # Check policy assignment
   vault token lookup
   vault policy read atom-policy
   ```

2. **"Connection refused" errors**
   ```bash
   # Check Vault server status
   vault status
   curl -k $VAULT_ADDR/v1/sys/health
   ```

3. **"Secret not found" errors**
   ```bash
   # List available secrets
   vault kv list secret/atom/
   vault kv get secret/atom/cosign
   ```

### Debug Commands

```bash
# Test Vault client
python -c "from services.workflow_registry.secrets import create_vault_client; print(create_vault_client().health_check())"

# Check environment
env | grep VAULT

# Validate AppRole
vault auth -method=approle role_id=$VAULT_ROLE_ID secret_id=$VAULT_SECRET_ID
```

## Production Deployment

### 1. High Availability

- Deploy Vault in HA mode
- Use external storage backend (Consul, etcd)
- Implement backup and disaster recovery

### 2. Security Hardening

- Enable TLS encryption
- Use auto-unsealing (AWS KMS, Azure Key Vault)
- Implement network segmentation
- Regular security audits

### 3. Monitoring

- Vault metrics in Prometheus
- Grafana dashboards
- Alerting on secret access patterns
- Log aggregation and analysis

## References

- [Vault Documentation](https://www.vaultproject.io/docs)
- [Vault Kubernetes Integration](https://www.vaultproject.io/docs/platform/k8s)
- [Vault Agent](https://www.vaultproject.io/docs/agent)
- [Vault CSI Provider](https://secrets-store-csi-driver.sigs.k8s.io/concepts.html#provider-for-the-secrets-store-csi-driver)