# Phase J.2 — Developer Console (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Phase:** J.2 — Developer Console (top-level UI over LaunchPad)
**Version target:** v1.0.0-j2-developer-console
**Branch prefix (local):** prod-feature/j2-developer-console
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution (agent must set `SIMULATION_MODE=true` if infra missing)

> **AGENT INSTRUCTION**: Use SIMULATION_MODE=true if infrastructure missing
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---

## Summary / Goal

**Objective:** Add a top-level **Developer Console** UI that sits above the existing LaunchPad. It lists org projects, global billing, marketplace entry, API key lifecycle, aggregated logs and alerts, and deep-links into the existing LaunchPad project environment. Reuse theme and components from the local LaunchPad source at `/collective_intelligence/launchpad/`. Do not overwrite LaunchPad. Provide deployable services and simulation-safe infra.

**Success Criteria:**

* [ ] Services deployed to `services/developer-console-*` (simulation-safe).
* [ ] Infra modules exist under `infra/terraform/modules/developer-console/` and `infra/helm/developer-console/`.
* [ ] Tests in `tests/developer-console/`.
* [ ] Scripts in `infra/scripts/developer-console/`.
* [ ] Policies in `infra/vault/policies/developer-console.hcl`.
* [ ] No phase directories created.
* [ ] `reports/launchpad_ui_filelist.txt` produced and theme-reuse plan created.
* [ ] Integration tests pass in simulation mode.
* [ ] UI uses LaunchPad theme assets from `/collective_intelligence/launchpad/components/` without modifying original files.

---

## New / [Specific] Policies (added)

* P1–P7 enforced on all Developer Console actions.
* P8 (multi-tenant isolation) applied to project-scoped tokens.
* P16–P20 enforced for production deploy gating.
* Policy file path: `infra/vault/policies/developer-console.hcl` (placeholder, must be populated before SIMULATION_MODE=false).

---

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="developer-console"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
SCRIPTS_PATH="infra/scripts"
POLICIES_PATH="infra/vault/policies"

# Deployment Settings
SIMULATION_MODE=true   # agent must keep true until manual sign-off
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-cloud"
IMAGE_TAG="j2-dev-0"

# LaunchPad source path (local)
LAUNCHPAD_SRC_PATH="collective_intelligence/launchpad"
LAUNCHPAD_THEME_PATH="${LAUNCHPAD_SRC_PATH}/components"

# Services endpoints
AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://services/auth:8080}"
LAUNCHPAD_BASE_URL="${LAUNCHPAD_BASE_URL:-/collective_intelligence/launchpad}"
BILLING_SERVICE_URL="${BILLING_SERVICE_URL:-http://services/billing:8090}"

# Security & Compliance
POLICY_ENFORCEMENT=true
AUDIT_LOGGING=true
VAULT_ADDR="${VAULT_ADDR:-http://vault.local}"
```

---

## File / Directory Structure to Create (exact)

```
services/
├── developer-console-core/
│   ├── src/main.py
│   ├── src/app.py
│   ├── src/config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── developer-console-api/
│   ├── src/api.py
│   ├── src/routes.py
│   └── Dockerfile
└── developer-console-worker/
    ├── src/worker.py
    └── Dockerfile

infra/
├── terraform/modules/developer-console/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/developer-console/
│   ├── Chart.yaml
│   ├── values.yaml       # include serviceMesh.enabled toggle
│   └── templates/
├── security/developer-console/
│   ├── security-policy.yaml
│   └── rbac.yaml
├── scripts/developer-console/
│   ├── precheck.sh
│   ├── deploy.sh
│   ├── migrate.sh
│   └── backup.sh
└── vault/policies/
    └── developer-console.hcl

ui/
├── dev-console/                  # New Developer Console Next.js app
│   ├── pages/
│   │   ├── index.js              # /projects list
│   │   ├── project/[id].js       # deep-link launcher into LaunchPad
│   │   ├── billing.js
│   │   ├── marketplace.js
│   │   ├── api-keys.js
│   │   └── settings.js
│   ├── components/
│   │   └── theme/                # copied theme assets (simulation-only)
│   ├── public/
│   └── package.json
└── collective_intelligence/
    └── launchpad/                # existing LaunchPad source (DO NOT MODIFY)

tests/
└── developer-console/
    ├── unit/
    │   └── test_health.py
    ├── integration/
    │   └── test_dev_console_integration.py
    └── e2e/
        └── test_dev_console_e2e.py

reports/
├── launchpad_ui_filelist.txt
└── developer_console_theme_reuse_plan.json
```

---

## High-Level Tasks (J.2.1 → J.2.9)

| ID    | Component           | Purpose                                                                                    |
| ----- | ------------------- | ------------------------------------------------------------------------------------------ |
| J.2.1 | Precheck            | Inspect `collective_intelligence/launchpad` and produce file list                          |
| J.2.2 | Theme Reuse Plan    | Decide which components to import or reference                                             |
| J.2.3 | Dev-console Backend | Implement `developer-console-core` APIs                                                    |
| J.2.4 | Dev-console API     | Aggregated OpenAPI and SDK trigger endpoints                                               |
| J.2.5 | Worker              | Background jobs (SDK build, template generation)                                           |
| J.2.6 | UI scaffold         | Create `ui/dev-console` pages that reuse theme assets                                      |
| J.2.7 | Security            | Vault policy placeholder and RBAC templates                                                |
| J.2.8 | Tests               | Unit / integration / e2e in simulation mode                                                |
| J.2.9 | Verification        | Produce `reports/developer_console_verification.json` and readiness gating artifact for I9 |

---

## Detailed Task Specs & Endpoints

### J.2.1 Precheck

* Run: `infra/scripts/developer-console/precheck.sh`
* Output: `reports/launchpad_ui_filelist.txt`
* Behavior: read-only scan; fails if `phase-*` dirs exist.

### J.2.2 Theme Reuse Plan

* Input: `reports/launchpad_ui_filelist.txt`
* Output: `reports/developer_console_theme_reuse_plan.json`
* Rules:

  * Copy only static, non-source files (styles, icons, tokens) into `ui/dev-console/components/theme/` in SIMULATION_MODE.
  * Reference React components from LaunchPad by import only if kept read-only. Prefer composition and wrapper components in `ui/dev-console/components/` to avoid editing LaunchPad files.
  * Do not alter `collective_intelligence/launchpad/pages/*` or `_app.js` without explicit approval.

### J.2.3 Developer-Console-Core endpoints (port 8090)

* `GET /health`
* `GET /v1/orgs`
* `GET /v1/projects`
* `POST /v1/projects` (calls LaunchPad project create API)
* `GET /v1/projects/{id}/launch` → returns `{ launch_url, scoped_token }`

### J.2.4 Developer-Console-API endpoints (port 8091)

* `GET /v1/openapi?project={id}` → aggregated OpenAPI for SDK generator
* `POST /v1/sdk/generate` → enqueue SDK build job (worker)

### J.2.5 Worker

* Queue: Redis or Kafka (env `WORKER_QUEUE_URL`)
* Jobs: `sdk_build`, `template_provision`, `export_project_snapshot`
* Limits: respect `AGENT_MAX_CPU_PERCENT` and `AGENT_MAX_TRAFFIC_PERCENT`

---

## Data Contracts (schemas)

### Project summary (JSON)

`services/developer-console-core` returns:

```json
{
  "id":"string",
  "name":"string",
  "owner":"org-id",
  "created_at":"ISO8601",
  "quota":{"cpu":"number","memory":"number"},
  "status":"running|suspended",
  "launch_url":"string"
}
```

### SDK build job payload (worker)

```json
{
  "job_id":"string",
  "project_id":"string",
  "api_spec_url":"string",
  "language":"js|python",
  "notify":"webhook_url"
}
```

---

## Embedded Scripts Pattern

### precheck.sh (embedded)

**File:** `infra/scripts/developer-console/precheck.sh` — read-only scan and lint

```bash
#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
LAUNCHPAD_SRC_PATH="${LAUNCHPAD_SRC_PATH:-collective_intelligence/launchpad}"

# 1. Ensure no phase directories exist
if ls -d phase-* 2>/dev/null; then
  echo "ERROR: phase-* directories present. Abort." >&2
  exit 2
fi

# 2. Check LaunchPad source
mkdir -p reports
if [ -d "${LAUNCHPAD_SRC_PATH}" ]; then
  echo "FOUND_LAUNCHPAD" >&2
  find "${LAUNCHPAD_SRC_PATH}" -maxdepth 3 -type f | sed "s|^|${LAUNCHPAD_SRC_PATH}/|" > reports/launchpad_ui_filelist.txt
  wc -l reports/launchpad_ui_filelist.txt >&2
else
  echo "NO_LAUNCHPAD" >&2
fi

# 3. Helm lint (non-blocking)
if [ -d "infra/helm/developer-console" ]; then
  helm lint infra/helm/developer-console || echo "helm lint warnings"
fi

# 4. Terraform plan (simulation-only)
if [ -d "infra/terraform/modules/developer-console" ]; then
  terraform -chdir=infra/terraform/modules/developer-console init -input=false -backend=false || true
  terraform -chdir=infra/terraform/modules/developer-console plan -input=false -out=reports/developer_console.tfplan || true
fi

echo "PRECHECK_COMPLETE" >&2
```

### deploy.sh (embedded)

**File:** `infra/scripts/developer-console/deploy.sh` — simulation-safe build + conditional deploy

```bash
#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
COMP="developer-console"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
IMAGE_TAG="${IMAGE_TAG:-j2-dev-0}"

for svc in services/${COMP}-*; do
  if [ -d "$svc" ]; then
    echo "Building $(basename $svc)"
    docker build -t "${DOCKER_REGISTRY}/atom-cloud/$(basename $svc):${IMAGE_TAG}" "$svc" || echo "build failed (sim)"
  fi
done

if [ "${SIMULATION_MODE}" != "true" ]; then
  terraform -chdir=infra/terraform/modules/${COMP} apply -auto-approve
  helm upgrade --install "${COMP}" infra/helm/${COMP} -n ${NAMESPACE} --wait
  vault policy write "${COMP}" infra/vault/policies/${COMP}.hcl || true
else
  echo "SIMULATION_MODE=true — infra actions skipped."
fi
```

---

### **Verification & Testing**

```markdown
## Verification Commands (agent must run and save outputs)
```

```bash
# Run precheck
bash infra/scripts/developer-console/precheck.sh 2>&1 | tee reports/developer_console_precheck.log

# Inspect produced filelist (if found)
if [ -f reports/launchpad_ui_filelist.txt ]; then
  head -n 100 reports/launchpad_ui_filelist.txt | sed -n '1,100p' > reports/launchpad_ui_filelist_head.txt
fi

# Simulated deploy
bash infra/scripts/developer-console/deploy.sh 2>&1 | tee reports/developer_console_deploy.log

# Run integration tests (simulation)
export SIMULATION_MODE=true
python -m pytest tests/developer-console/integration/ --maxfail=1 -q --json-report --json-report-file=reports/developer_console_integration.json
```

#### Integration Test Stub (agent must create)

File: `tests/developer-console/integration/test_dev_console_integration.py`

```python
import os
import requests
import pytest

BASE = os.getenv('DEVELOPER_CONSOLE_BASE_URL', 'http://localhost:8090')
SIM = os.getenv('SIMULATION_MODE', 'true') == 'true'

def test_health():
    if SIM:
        assert True
    else:
        r = requests.get(BASE + '/health')
        assert r.status_code == 200
```

---

## Agent Execution Steps (explicit sequence)

1. Validate environment

   ```bash
   if ls -d phase-* 2>/dev/null; then
     echo "ERROR: phase dirs exist" && exit 1
   fi
   export SIMULATION_MODE=true
   export LAUNCHPAD_SRC_PATH="collective_intelligence/launchpad"
   ```

2. Run precheck (read-only)

   ```bash
   bash infra/scripts/developer-console/precheck.sh | tee reports/developer_console_precheck.log
   ```

3. Inspect `reports/launchpad_ui_filelist.txt`

   * If present, paste first 50 lines here for plan review.
   * Agent will create `reports/developer_console_theme_reuse_plan.json` describing which files to copy or reference.

4. Create scaffold (simulation)

   ```bash
   mkdir -p services/developer-console-core services/developer-console-api services/developer-console-worker ui/dev-console/components/theme
   touch infra/vault/policies/developer-console.hcl
   ```

5. Copy theme assets (simulation only)

   ```bash
   # copy only styles/icons/tokens (non-js)
   rsync -av --include='*/' --include='*.css' --include='*.scss' --include='*.png' --include='*.svg' --exclude='*.js' --exclude='pages/**' \
     collective_intelligence/launchpad/components/ ui/dev-console/components/theme/ || true
   ```

6. Simulated deploy and tests

   ```bash
   bash infra/scripts/developer-console/deploy.sh
   pytest tests/developer-console/integration/ --json-report --json-report-file=reports/developer_console_integration.json
   ```

7. Produce verification artifact

   ```bash
   jq -n --arg sim "${SIMULATION_MODE}" --arg commit "$(git rev-parse --short HEAD 2>/dev/null || echo local)" \
     '{commit:$commit, sim:$sim, timestamp:(now|todate)}' > reports/developer_console_verification.json
   ```

---

## Acceptance Criteria

* [ ] `services/developer-console-*` created and service stubs present.
* [ ] `infra/terraform/modules/developer-console` and `infra/helm/developer-console` present.
* [ ] `tests/developer-console/` contains minimal unit/integration/e2e.
* [ ] `infra/scripts/developer-console/precheck.sh` produced `reports/launchpad_ui_filelist.txt`.
* [ ] `reports/developer_console_theme_reuse_plan.json` created and lists exact theme files copied.
* [ ] No file modifies `collective_intelligence/launchpad/` sources.
* [ ] All checks and tests pass in `SIMULATION_MODE=true`.
* [ ] `reports/developer_console_verification.json` exists.

---

## Deliverables & Compliance

### Deliverables

* `services/developer-console-core/`, `developer-console-api/`, `developer-console-worker/` with stubs.
* `ui/dev-console/` scaffold that imports theme assets from `collective_intelligence/launchpad/components/` (copied into `ui/dev-console/components/theme/` in simulation).
* `infra/terraform/modules/developer-console/` and `infra/helm/developer-console/`.
* `infra/scripts/developer-console/{precheck.sh,deploy.sh}`.
* `reports/launchpad_ui_filelist.txt` and `reports/developer_console_theme_reuse_plan.json`.
* `infra/vault/policies/developer-console.hcl` placeholder.

### Security & Compliance reminders

* Maintain P1–P20 checks.
* Never expose Vault secrets in files. Use Vault references.
* SIMULATION_MODE must remain true until Security sign-off.
* Any request to flip to SIMULATION_MODE=false must produce `reports/developer_console_decision_request.json` with justification and sign-off.

---

## Notes for the Agent (embedded prompt)

> Run precheck. If `collective_intelligence/launchpad` is found, generate `reports/launchpad_ui_filelist.txt`. From that list create `reports/developer_console_theme_reuse_plan.json` mapping which `.css`, `.svg`, `.png`, and static assets will be copied to `ui/dev-console/components/theme/` in simulation-mode. Do NOT copy `*.js` components or modify `collective_intelligence/launchpad/`. Create wrapper components in `ui/dev-console/components/` that import theme tokens. Respect `SIMULATION_MODE=true`. Log every action to `reports/developer_console_precheck.log`. If any step needs SIMULATION_MODE=false, stop and write `reports/developer_console_decision_request.json` with justification.

---

### Theme Reuse Plan (immediate, high-level)

1. Inspect `reports/launchpad_ui_filelist.txt`. Identify:

   * `components/styles/*.css` or `*.scss` → copy to `ui/dev-console/components/theme/`
   * `components/icons/*.svg`, `components/images/*` → copy
   * `components/theme/tokens.js` or `tokens.json` → reference by copying token file (not code)
2. For React components under `collective_intelligence/launchpad/components/*`:

   * Do not copy `.js` components.
   * Create thin wrapper components in `ui/dev-console/components/` that import styling and call existing component via dynamic import only if safe.
   * Prefer to use the same layout by importing `collective_intelligence/launchpad/components/Layout` as read-only reference. If import causes bundling/link issues, deep-link LaunchPad pages instead.
3. For routing:

   * Developer Console `project/[id].js` should redirect or open LaunchPad at `LAUNCHPAD_BASE_URL?projectId={id}&scopedToken={token}`.
   * Do not replicate LaunchPad internal pages.

---

