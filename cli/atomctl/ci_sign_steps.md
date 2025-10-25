# CI Integration for WPK Signing

## GitHub Actions
```yaml
- name: Sign WPK
  env:
    COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
  run: |
    echo "$COSIGN_PRIVATE_KEY" > cosign.key
    atomctl sign workflow.wpk.yaml --key cosign.key
    atomctl push workflow.wpk.yaml --registry $REGISTRY_URL
```

## GitLab CI
```yaml
sign_wpk:
  script:
    - echo "$COSIGN_PRIVATE_KEY" > cosign.key
    - atomctl sign workflow.wpk.yaml --key cosign.key
    - atomctl push workflow.wpk.yaml --registry $REGISTRY_URL
```

## Security Notes
- Store private keys in secure CI secrets
- Use different keys per environment
- Rotate keys quarterly