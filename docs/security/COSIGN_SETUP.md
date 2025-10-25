# Cosign Setup and WPK Signing Guide

## Overview

ATOM enforces cosign signature verification for all WPK (Workflow Package) uploads to ensure supply chain security. This document explains how to set up cosign keys and sign WPK packages.

## Prerequisites

- cosign binary installed (`go install github.com/sigstore/cosign/v2/cmd/cosign@latest`)
- Access to ATOM workflow registry
- Valid WPK package to sign

## Key Generation

### 1. Generate Cosign Key Pair

```bash
# Generate new key pair
cosign generate-key-pair

# This creates:
# - cosign.key (private key - keep secure!)
# - cosign.pub (public key - share with registry)
```

### 2. Configure Registry Public Key

```bash
# Set public key path for registry
export COSIGN_PUBLIC_KEY_PATH=/path/to/cosign.pub

# Or in .env file
echo "COSIGN_PUBLIC_KEY_PATH=/path/to/cosign.pub" >> .env
```

## Signing WPK Packages

### 1. Sign WPK File

```bash
# Sign your WPK package
cosign sign-blob --key cosign.key --output-signature restart-unhealthy.wpk.sig restart-unhealthy.wpk.yaml

# The signature file contains the base64 encoded signature
cat restart-unhealthy.wpk.sig
```

### 2. Add Signature to WPK Metadata

Edit your WPK file to include the signature:

```yaml
apiVersion: v1
kind: WorkflowPackage
metadata:
  name: restart-unhealthy
  version: 1.0.0
  description: Restart unhealthy pods
  author: ops-team
  signature: |
    MEUCIQDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==
spec:
  # ... rest of WPK spec
```

### 3. Upload Signed WPK

```bash
# Upload to registry
curl -X POST http://localhost:8000/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@restart-unhealthy.wpk.yaml"
```

## Verification Process

The registry automatically:

1. **Extracts signature** from WPK metadata
2. **Validates format** (base64 encoded)
3. **Verifies signature** using configured public key
4. **Rejects unsigned** or invalid packages

## Development Mode

For development/testing, you can disable signature enforcement:

```bash
export ATOM_DEV_MODE=true
```

**⚠️ WARNING: Never use development mode in production!**

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Sign and Push WPK
on:
  push:
    paths: ['examples/playbooks/*.wpk.yaml']

jobs:
  sign-wpk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install cosign
        uses: sigstore/cosign-installer@v3
        
      - name: Sign WPK
        env:
          COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
          COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
        run: |
          echo "$COSIGN_PRIVATE_KEY" > cosign.key
          cosign sign-blob --key cosign.key --output-signature wpk.sig examples/playbooks/restart-unhealthy.wpk.yaml
          
      - name: Update WPK with signature
        run: |
          SIG=$(cat wpk.sig)
          yq eval '.metadata.signature = strenv(SIG)' -i examples/playbooks/restart-unhealthy.wpk.yaml
          
      - name: Push to registry
        run: |
          curl -X POST $REGISTRY_URL/workflows \
            -H "Authorization: Bearer $REGISTRY_TOKEN" \
            -F "file=@examples/playbooks/restart-unhealthy.wpk.yaml"
```

## Security Best Practices

1. **Private Key Security**
   - Store private keys in secure key management (Vault, AWS KMS)
   - Never commit private keys to version control
   - Use different keys for different environments

2. **Key Rotation**
   - Rotate keys regularly (quarterly recommended)
   - Update registry public key configuration
   - Re-sign existing WPK packages

3. **Access Control**
   - Limit who can sign WPK packages
   - Use separate keys for different teams/projects
   - Audit signature operations

## Troubleshooting

### Common Issues

1. **"cosign binary not found"**
   ```bash
   # Install cosign
   go install github.com/sigstore/cosign/v2/cmd/cosign@latest
   # Or download from releases
   ```

2. **"Invalid signature format"**
   - Ensure signature is base64 encoded
   - Check for extra whitespace/newlines
   - Verify signature was generated correctly

3. **"Public key not found"**
   - Check COSIGN_PUBLIC_KEY_PATH environment variable
   - Verify public key file exists and is readable
   - Ensure correct key format

### Debug Commands

```bash
# Verify signature manually
cosign verify-blob --key cosign.pub --signature wpk.sig wpk.yaml

# Check registry configuration
curl http://localhost:8000/health

# Test with development mode
ATOM_DEV_MODE=true python services/workflow-registry/main.py
```

## References

- [Cosign Documentation](https://docs.sigstore.dev/cosign/overview/)
- [Sigstore Project](https://www.sigstore.dev/)
- [Supply Chain Security Best Practices](https://slsa.dev/)