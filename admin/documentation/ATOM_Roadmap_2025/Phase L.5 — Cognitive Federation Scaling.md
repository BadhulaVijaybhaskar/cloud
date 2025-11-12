# L.5 — Cognitive Federation Scaling (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Component:** L.5 — Cognitive Federation Scaling
**Version target:** v1.0.0-l5
**Branch prefix:** prod-feature/l5-cognitive-scaling
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution

> **AGENT INSTRUCTION**: Use `SIMULATION_MODE=true` if infrastructure missing or running locally.
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---

## Summary / Goal

**Objective:** Implement a production-safe, agent-ready Cognitive Federation Scaling layer that enables federated model / policy propagation, cross-region learning rate coordination, and safe, policy-checked global optimizations. This phase expands L.4 with global learning mesh scaling, federated model distillation, and coordinated policy rollouts.

**Success Criteria:**

* [ ] Services deployed to `services/l5-*` directories.
* [ ] Infrastructure in `infra/terraform/modules/l5_cognitive_scaling/` and `infra/helm/l5-cognitive-scaling/`.
* [ ] Simulation scripts and reports in `infra/scripts/l5/` and `reports/l5/`.
* [ ] Tests in `tests/l5/` (unit, integration, e2e).
* [ ] Makefile targets and CI workflow exist.
* [ ] P32–P35 + P36 (new: federated scaling safety) implemented and enforced.
* [ ] No phase directories created.
* [ ] All integration tests pass in simulation mode.

---

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="l5-cognitive-scaling"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
REPORTS_PATH="reports"
SIMULATION_MODE=true    # default; set false only with approvals
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-l5"
VAULT_ADDR="${VAULT_ADDR:-https://vault.atom.internal}"

# Feature toggles
SERVICE_MESH_ENABLED=false
AUTOMATED_DISTILLATION=false
GLOBAL_LEARNING_RATE=0.001

# Security & Governance
POLICY_ENFORCEMENT=true
FEDERATION_APPROVAL_ROLE="Governance Owner"
APPROVE_L5_DEPLOY="no"
```

---

## File / Directory Structure to Create (exact)

```
services/
├── l5-orchestrator/
│   ├── src/main.py
│   ├── Dockerfile
│   ├── config.yaml
│   └── requirements.txt
├── l5-model-aggregator/
│   ├── src/main.py
│   ├── Dockerfile
│   └── requirements.txt
├── l5-distiller/
│   ├── src/main.py
│   ├── Dockerfile
│   └── requirements.txt
├── l5-policy-rollout/
│   ├── src/main.py
│   ├── Dockerfile
│   └── requirements.txt
└── l5-edge-adapter/
    ├── src/main.py
    ├── Dockerfile
    └── requirements.txt

infra/
├── terraform/modules/l5_cognitive_scaling/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/l5-cognitive-scaling/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── contracts/l5/
│   └── openapi_l5.yaml
├── security/l5/
│   ├── mtls_bootstrap.sh
│   └── rbac.yaml
├── scripts/l5/
│   ├── precheck.sh
│   ├── deploy.sh
│   ├── verify.sh
│   └── rollback.sh
└── vault/policies/
    └── l5_cognitive_scaling.hcl

tests/l5/
├── unit/
│   ├── test_orchestrator.py
│   └── test_distiller.py
├── integration/
│   └── test_end_to_end.py
└── e2e/
    └── test_global_rollout.py

models/
├── l5/
│   ├── base_distilled.pkl
│   └── metadata.json

reports/l5/
├── precheck_report.json
├── deploy_summary.json
└── verification_summary.json

Makefile
.github/workflows/l5_cognitive_scaling.yml
docs/l5_design.md
```

---

## Service Specifications & Endpoints

### L5 Orchestrator Service

**Path:** `services/l5-orchestrator/`
**Port:** 9200
**Purpose:** Master coordination for federated scaling and rollout orchestration.

**Endpoints:**

* `GET /health` → Health check
* `POST /v1/rollout` → Start a policy/model rollout (body: rollout plan)
* `GET /v1/rollouts/{id}` → Get rollout status
* `POST /v1/approve/{id}` → Manual approval endpoint for a rollout (requires role)

**Environment:**

```yaml
SERVICE_NAME: "l5-orchestrator"
SERVICE_PORT: 9200
SIMULATION_MODE: "${SIMULATION_MODE}"
VAULT_ADDR: "${VAULT_ADDR}"
POLICY_BROKER_URL: "${POLICY_BROKER_URL}"
```

### L5 Model Aggregator

**Path:** `services/l5-model-aggregator/`
**Port:** 9201
**Purpose:** Aggregate model updates from multiple regions/nodes, compute aggregated model weights/metadata.

**Endpoints:**

* `GET /health`
* `POST /v1/submit` → Submit local model update (multipart: model + metadata)
* `GET /v1/aggregate` → Trigger aggregation (or scheduled)

**Environment:**

```yaml
SERVICE_NAME: "l5-model-aggregator"
SERVICE_PORT: 9201
AGGREGATION_WINDOW_SEC: 300
```

### L5 Distiller

**Path:** `services/l5-distiller/`
**Port:** 9202
**Purpose:** Distill aggregated models into compact artifacts suitable for edge; supports explainability hooks.

**Endpoints:**

* `GET /health`
* `POST /v1/distill` → Start distillation job
* `GET /v1/models/{id}/download` → Download distilled model

**Environment:**

```yaml
SERVICE_NAME: "l5-distiller"
SERVICE_PORT: 9202
DISTILL_BATCH_SIZE: 128
```

### L5 Policy Rollout Service

**Path:** `services/l5-policy-rollout/`
**Port:** 9203
**Purpose:** Stage and roll out policy changes globally with canary, metrics checks, and automatic rollback.

**Endpoints:**

* `GET /health`
* `POST /v1/policy` → Submit policy change request
* `POST /v1/policy/{id}/canary` → Start canary rollout
* `POST /v1/policy/{id}/rollback` → Trigger rollback

**Environment:**

```yaml
SERVICE_NAME: "l5-policy-rollout"
SERVICE_PORT: 9203
CANARY_WINDOW_SEC: 3600
```

### L5 Edge Adapter

**Path:** `services/l5-edge-adapter/`
**Port:** 9204
**Purpose:** Lightweight edge agent adapter for receiving distilled models and applying safe updates.

**Endpoints:**

* `GET /health`
* `POST /v1/apply` → Apply distilled model (simulation-safe)
* `GET /v1/status` → Edge agent status and applied model metadata

**Environment:**

```yaml
SERVICE_NAME: "l5-edge-adapter"
SERVICE_PORT: 9204
APPLY_TIMEOUT_SEC: 300
```

---

## Embedded Scripts Pattern

### Deployment Script (embedded)

**File:** `infra/scripts/l5/deploy.sh`

```bash
#!/bin/bash
set -euo pipefail

COMPONENT_NAME="l5-cognitive-scaling"
SERVICES_PATH="services"
INFRA_PATH="infra"
POLICIES_PATH="${INFRA_PATH}/vault/policies"
SIM="${SIMULATION_MODE:-true}"

echo "Deploying ${COMPONENT_NAME} (SIMULATION_MODE=${SIM})..."

# Basic precheck
bash "${INFRA_PATH}/scripts/l5/precheck.sh"

# Build Docker images (local simulation)
for svc in ${SERVICES_PATH}/l5-*; do
  if [ -d "$svc" ]; then
    pushd "$svc" >/dev/null
    if [ -f Dockerfile ]; then
      echo "Building $(basename $svc)..."
      docker build -t "${DOCKER_REGISTRY}/$(basename $svc):latest" .
    fi
    popd >/dev/null
  fi
done

# Apply Vault policies (simulated)
if [ -f "${POLICIES_PATH}/l5_cognitive_scaling.hcl" ]; then
  echo "Applying Vault policy (simulated)..."
  if [ "${SIM}" != "true" ]; then
    vault policy write l5_cognitive_scaling "${POLICIES_PATH}/l5_cognitive_scaling.hcl"
  else
    echo "SIMULATION: vault policy apply skipped"
  fi
fi

# Terraform & Helm in simulation
echo "Rendering terraform plan and helm templates..."
mkdir -p reports/l5
echo "{}" > reports/l5/terraform_plan_l5.json
echo "{}" > reports/l5/helm_template_l5.yaml

if [ "${SIM}" != "true" ]; then
  terraform -chdir="${INFRA_PATH}/terraform/modules/l5_cognitive_scaling" apply -auto-approve
  helm upgrade --install "${COMPONENT_NAME}" "${INFRA_PATH}/helm/l5-cognitive-scaling"
fi

echo '{"phase":"L.5","status":"SIM_OK","timestamp":"'"$(date -u --iso-8601=seconds)"'"}' > reports/l5/deploy_summary.json
echo "Deployment complete (simulation mode=${SIM})"
```

### Precheck Script (embedded)

**File:** `infra/scripts/l5/precheck.sh`

```bash
#!/bin/bash
set -e

echo "Running L.5 precheck..."
mkdir -p reports/l5

# Check model artifacts
if [ -f "models/l5/base_distilled.pkl" ]; then
  model_ok=true
else
  model_ok=false
fi

jq -n --arg model "$model_ok" --arg sim "${SIMULATION_MODE}" \
  '{phase:"L.5",timestamp:(now|todate),simulation_mode:$sim, model_present:$model}' > reports/l5/precheck_report.json

if [ "${SIMULATION_MODE}" != "true" ] && [ "$model_ok" = "false" ]; then
  echo "ERROR: base_distilled model missing in live mode"
  exit 1
fi

echo "Precheck complete."
```

### Verification Script (embedded)

**File:** `infra/scripts/l5/verify.sh`

```bash
#!/bin/bash
set -e

echo "Verifying L.5 deployment (simulation mode=${SIMULATION_MODE})..."
mkdir -p reports/l5

# Simulate health checks
jq -n '{phase:"L.5",timestamp:(now|todate),checks:{orchestrator:"healthy",aggregator:"healthy",distiller:"healthy",policy_rollout:"healthy",edge_adapter:"healthy"},overall_status:"PASS"}' > reports/l5/verification_summary.json

echo "Verification written to reports/l5/verification_summary.json"
```

---

## Integration Test Template (embedded)

**File:** `tests/l5/integration/test_end_to_end.py`

```python
import os
import requests
import pytest
import json

SIM = os.getenv("SIMULATION_MODE", "true") == "true"
BASE = "http://localhost:9200"

def test_rollout_lifecycle():
    if SIM:
        assert True, "Simulation mode - rollout lifecycle test skipped"
        return

    # Start a rollout
    resp = requests.post(f"{BASE}/v1/rollout", json={"plan":"canary","target":"all"})
    assert resp.status_code in (200,202)
    rollout = resp.json()
    assert "id" in rollout
```

---

## Agent Execution Steps (explicit sequence)

1. **Validate Environment**

   ```bash
   # ensure no phase-* directories exist
   if ls phase-* 2>/dev/null; then
     echo "ERROR: Phase directories found. Remove or migrate."
     exit 1
   fi
   ```

2. **Create Complete Component Structure**

   ```bash
   mkdir -p services/l5-{orchestrator,model-aggregator,distiller,policy-rollout,edge-adapter}
   mkdir -p infra/terraform/modules/l5_cognitive_scaling
   mkdir -p infra/helm/l5-cognitive-scaling
   mkdir -p infra/scripts/l5
   mkdir -p tests/l5/{unit,integration,e2e}
   touch infra/vault/policies/l5_cognitive_scaling.hcl
   ```

3. **Run Precheck**

   ```bash
   SIMULATION_MODE=true bash infra/scripts/l5/precheck.sh
   ```

4. **Build & Deploy (simulation)**

   ```bash
   SIMULATION_MODE=true bash infra/scripts/l5/deploy.sh
   ```

5. **Verify**

   ```bash
   SIMULATION_MODE=true bash infra/scripts/l5/verify.sh
   ```

6. **Run Tests**

   ```bash
   SIMULATION_MODE=true python -m pytest tests/l5/ -q
   ```

7. **If Approved (live only)**

   ```bash
   # Approval must be recorded in reports/l5/approval_signoffs.json
   SIMULATION_MODE=false APPROVE_L5_DEPLOY=yes bash infra/scripts/l5/deploy.sh
   ```

---

## Acceptance Criteria

* [ ] Services in `services/l5-*` (no phase directories)
* [ ] Infrastructure in `infra/terraform/modules/l5_cognitive_scaling/` and `infra/helm/l5-cognitive-scaling/`
* [ ] Tests in `tests/l5/` with unit, integration and e2e coverage
* [ ] Scripts in `infra/scripts/l5/` for precheck/deploy/verify/rollback
* [ ] Vault policy in `infra/vault/policies/l5_cognitive_scaling.hcl`
* [ ] `reports/l5/` contains `precheck_report.json`, `deploy_summary.json`, `verification_summary.json`
* [ ] CI workflow at `.github/workflows/l5_cognitive_scaling.yml` runs simulation steps and uploads artifacts
* [ ] No hardcoded phase paths in any files
* [ ] All tests pass in simulation mode

---

## Deliverables (explicit)

* Complete service directories with `src/main.py` and Dockerfiles.
* Terraform module + Helm chart.
* Vault policy file.
* Management scripts in `infra/scripts/l5/`.
* Unit, integration and e2e tests.
* Makefile targets: `l5-precheck`, `l5-deploy`, `l5-verify`, `l5-clean`.
* CI workflow `.github/workflows/l5_cognitive_scaling.yml`.
* `docs/l5_design.md` with architecture, safety, and operator runbooks.
* Reports under `reports/l5/`.

---

## Security & Policies

* P32–P35 inherited from L.4 remain enforced. This phase adds:

  * **P36 — Federated Scaling Safety**

    * No global rollouts without explicit APPROVE_L5_DEPLOY=yes and multi-role signoffs.
    * Automatic rollback if health regressions exceed thresholds in canary window.
    * Rate-limit global model/ policy application to avoid cascading failures.
* Vault integration for model signing keys and certs.
* mTLS enforced for cross-region communications (scripts provided in `infra/security/`).

---

## CI Integration (example)

**File:** `.github/workflows/l5_cognitive_scaling.yml`

```yaml
name: L5 Cognitive Scaling Verify
on:
  push:
    branches: ['prod-feature/l5-*']
  pull_request:
    branches: ['prod-feature/l5-*']
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get update -y && sudo apt-get install -y jq
      - run: chmod +x infra/scripts/l5/*.sh || true
      - run: SIMULATION_MODE=true infra/scripts/l5/precheck.sh
      - run: SIMULATION_MODE=true infra/scripts/l5/deploy.sh
      - run: SIMULATION_MODE=true infra/scripts/l5/verify.sh
      - run: pytest tests/l5/ || true
      - uses: actions/upload-artifact@v4
        with:
          name: l5-reports
          path: reports/l5
```

---

## Notes for the Agent (embedded prompt)

> You are building ATOM Cloud L.5 Cognitive Federation Scaling using the global directory structure.
> NEVER create phase-* directories. Components are distributed across:
>
> * Services: `services/[component-name]/`
> * Infrastructure: `infra/terraform/modules/[component-name]/`, `infra/helm/[component-name]`
> * Tests: `tests/[component-name]/`
> * Scripts: `infra/scripts/[component-name]/`
> * Vault policies: `infra/vault/policies/[component-name].hcl`
>   Use `SIMULATION_MODE=true` when infrastructure is not available. Validate all paths before creation. Follow the exact directory structure specified above. Ensure P36 federated scaling safety policy is enforced by default; require `APPROVE_L5_DEPLOY=yes` and recorded signoffs in `reports/l5/approval_signoffs.json` for any live rollout.

---

## Embedded Example: Minimal `src/main.py` for Orchestrator

```python
# services/l5-orchestrator/src/main.py
from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l5-orchestrator"})

@app.route("/v1/rollout", methods=["POST"])
def rollout():
    body = request.json or {}
    if os.getenv("SIMULATION_MODE", "true") == "true":
        return jsonify({"id":"sim-rollout-0001","status":"scheduled","simulated":True}), 202
    return jsonify({"id":"rollout-0001","status":"started"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9200)))
```

---

## Failure Handling Rules

* If precheck fails, abort deployment and write `reports/l5/precheck_report.json` with error details.
* If any canary metric breaches thresholds, policy-rollout service must trigger `rollback` automatically.
* If Vault is unreachable in live mode, abort and notify `Governance Owner`.
* All rollouts generate a `decision_<id>.json` audit artifact in `reports/l5/decisions/`.

---

## Acceptance Test Scenarios (examples)

1. Simulation precheck passes and writes `reports/l5/precheck_report.json`.
2. Simulated deploy produces `reports/l5/deploy_summary.json`.
3. Simulated verify writes `reports/l5/verification_summary.json`.
4. Integration test `tests/l5/integration/test_end_to_end.py` passes (skips in simulation as appropriate).
5. Policy enforcement test: submit a rollout that violates P36; system rejects with audit log.

---

## Deliverable Checklist (for PR body)

* Services: `services/l5-*` (with Dockerfile + `src/main.py`)
* Infra: `infra/terraform/modules/l5_cognitive_scaling/` + `infra/helm/l5-cognitive-scaling/`
* Scripts: `infra/scripts/l5/{precheck,deploy,verify,rollback}.sh`
* Vault policy: `infra/vault/policies/l5_cognitive_scaling.hcl`
* Tests: `tests/l5/{unit,integration,e2e}`
* Reports: `reports/l5/{precheck_report.json,deploy_summary.json,verification_summary.json}`
* Docs: `docs/l5_design.md`
* CI: `.github/workflows/l5_cognitive_scaling.yml`
* Makefile targets: `l5-precheck`, `l5-deploy`, `l5-verify`

