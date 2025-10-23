# Naksha Cloud — Task 07: CI/CD Hardening & Secure Release Pipeline

---

## Goal
Secure the build-and-deploy process: signed images, gated production deploys, and automated smoke tests after release.

---

## 1. Prerequisites
- GitHub Actions or equivalent CI/CD available.
- Secrets configured in repository:
  | Secret | Purpose |
  |---------|----------|
  | `COSIGN_KEY` | Private key for image signing |
  | `GH_TOKEN` | GitHub authentication |
  | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | for Terraform / backups |
  | `KUBECONFIG_BASE64` | production kubeconfig for deploy jobs |

---

## 2. Cosign Image Signing

### Install Cosign (local or CI)
```bash
curl -sSL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 -o /usr/local/bin/cosign
chmod +x /usr/local/bin/cosign
```

### Update `.github/workflows/ci-cd.yaml`

Add after the build step:

```yaml
- name: Sign Docker image (LangGraph)
  run: cosign sign --key env://COSIGN_KEY ${{ env.DOCKER_IMAGE_LANGGRAPH }}
  env:
    COSIGN_KEY: ${{ secrets.COSIGN_KEY }}

- name: Sign Docker image (Vector)
  run: cosign sign --key env://COSIGN_KEY ${{ env.DOCKER_IMAGE_VECTOR }}
  env:
    COSIGN_KEY: ${{ secrets.COSIGN_KEY }}
```

Verification step:

```yaml
- name: Verify signed images
  run: |
    cosign verify --key env://COSIGN_KEY ${{ env.DOCKER_IMAGE_LANGGRAPH }}
    cosign verify --key env://COSIGN_KEY ${{ env.DOCKER_IMAGE_VECTOR }}
```

---

## 3. Policy Gate for Unsigned Images

Create admission policy (Kubernetes OPA Gatekeeper or Kyverno) example:

`infra/security/policy-signed-images.yaml`

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: enforce
  rules:
    - name: verify-signature
      match:
        resources:
          kinds:
            - Pod
      verifyImages:
        - imageReferences:
            - "docker.io/naksha/*"
          attestors:
            - entries:
              - keys:
                  publicKeys: |
                    -----BEGIN PUBLIC KEY-----
                    # your cosign.pub content
                    -----END PUBLIC KEY-----
```

Apply:

```bash
kubectl apply -f infra/security/policy-signed-images.yaml
```

---

## 4. Terraform Gated Deploy (Production Workspace)

Modify `.github/workflows/deploy-prod.yaml`:

```yaml
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Terraform Init & Plan
        run: terraform -chdir=infra/terraform init && terraform -chdir=infra/terraform plan
      - name: Upload Plan Artifact
        uses: actions/upload-artifact@v4
        with:
          name: tf-plan
          path: infra/terraform/tfplan.out

  apply:
    needs: [plan]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Manual approval gate
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ secrets.GH_TOKEN }}
          approvers: "repo-admins"
      - name: Terraform Apply
        run: terraform -chdir=infra/terraform apply -auto-approve
```

---

## 5. Post-Deploy Smoke Tests

`infra/scripts/smoke_test.sh`

```bash
#!/bin/bash
set -e
echo "Running post-deploy smoke tests..."
curl -fsSL https://langgraph.local/healthz
curl -fsSL https://grafana.local/login
curl -fsSL http://vector.vector.svc.cluster.local:8081/healthz
echo "Smoke tests passed."
```

Add to workflow after deploy:

```yaml
- name: Run smoke tests
  run: bash infra/scripts/smoke_test.sh
```

---

## 6. Reporting & Verification

Agent must:

* Commit workflow updates and policy manifests.
* Save CI/CD run results to `/reports/ci_cd_report.md`.
* Save workflow logs to `/reports/logs/ci_cd_pipeline.log`.
* Open PR: `prod-hardening/07-cicd-hardening`.

`/reports/ci_cd_report.md` must include:

* summary of changes
* signing & verification output
* gate policy validation result
* smoke test summary

---

## 7. Success Criteria

✅ Cosign successfully signs and verifies images.
✅ OPA/Kyverno policy blocks unsigned images.
✅ Terraform plan requires manual approval for production.
✅ Smoke tests run automatically post-deploy.
✅ Reports committed and PR created.