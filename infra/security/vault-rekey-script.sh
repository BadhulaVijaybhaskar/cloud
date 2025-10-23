#!/bin/bash
# Vault Key Rotation Script
set -e

echo "🔄 Starting Vault key rotation process..."

# Check Vault status
kubectl exec -n vault vault-0 -- vault status

# Generate new unseal keys (requires existing unseal keys)
echo "Generating new unseal keys..."
kubectl exec -n vault vault-0 -- vault operator rekey -init -key-shares=3 -key-threshold=2

# Rotate encryption key
echo "Rotating encryption key..."
kubectl exec -n vault vault-0 -- vault operator rotate

# Update app role tokens
echo "Regenerating app role tokens..."
kubectl exec -n vault vault-0 -- vault write -f auth/approle/role/langgraph/secret-id
kubectl exec -n vault vault-0 -- vault write -f auth/approle/role/vector/secret-id

echo "✅ Vault key rotation completed"