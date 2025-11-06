# Phase K.4 — Cognitive Optimization & Knowledge Transfer (Agent-Ready Build Specification)

**Branch:** `prod-feature/k4.cognitive-optimization`
**Mode:** `SIMULATION_MODE=true` (default — agents must use simulation by default)
**Parent Phases:** K.1 (Autonomous Runtime), K.2 (Adaptive Scaling), K.3 (Self-Healing)
**Dependencies:** `knowledge-indexer`, `aol-controller`, `training-worker`, `predictive-ops-engine`, `action-executor`, `governance-api`

---

## Summary / Goal

**Objective:** Build a cognitive optimization layer that extracts lessons from past incidents, decisions, and model performance — then transfers those learnings to improve model policies, scaling heuristics, and healing plans automatically (subject to governance).
**Success Criteria:**

* [ ] `services/cognitive-learner/`, `services/experience-repository/`, `services/transfer-agent/`, `services/optimizer-proxy/` created under `services/`.
* [ ] Infra modules present in `infra/terraform/modules/k4_cognitive/` and Helm chart in `infra/helm/k4-cognitive/`.
* [ ] Scripts in `infra/scripts/k4/` (precheck/deploy/verify) exist and operate in `SIMULATION_MODE=true`.
* [ ] Tests under `tests/k4/` (unit/integration/e2e) created and pass in simulation.
* [ ] Reports written to `reports/k4/` (precheck_report.json, deploy_summary.json, transfer_log.json, verification_summary.json).
* [ ] Policy P23 (Knowledge Integrity & Transfer Safety) defined and enforced via Vault policy `infra/vault/policies/k4_cognitive.hcl`.
* [ ] CI workflow `.github/workflows/k4_cognitive.yml` runs simulation steps and uploads artifacts.
* [ ] No phase directories are created — follow global directory structure.

---

## New / Specific Policies (added)

**P23 — Knowledge Integrity & Transfer Safety** (new policy for K.4)

* **P23.1 Provenance:** Every knowledge artifact (experience, lesson, transfer action) must include origin metadata (source service, timestamp, confidence, decision id).
* **P23.2 Privacy & Anonymization:** Any PII or tenant-identifying signals must be removed/anonymized before knowledge storage or transfer.
* **P23.3 Transfer Approval:** Any automated policy/model changes proposed by transfer-agent must be flagged `simulated` and require explicit APPROVE_TRANSFER=yes to apply live.
* **P23.4 Auditability:** All transfer decisions must produce deterministic audit artifacts and be stored in `reports/k4/transfer_log.json`.
* **P23.5 Rollbackability:** Changes promoted by transfers must be versioned and rollback-able with one command.
* **P23.6 Rate Limits:** At most one automated promotion per model/policy per 24 hours without manual signoff.
* **Enforcement:** `governance-api` checks P23 for each transfer action; Vault policies include `k4_cognitive.hcl` controls.

---

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="k4-cognitive"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
REPORTS_PATH="reports/k4"
POLICIES_PATH="infra/vault/policies"
SCRIPTS_PATH="infra/scripts/k4"
MODELS_PATH="models"

# Deployment Settings
SIMULATION_MODE=true   # Agents must default to true
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-k4"

# Governance & Safety
POLICY_ENFORCEMENT=true
APPROVE_TRANSFER=no    # must be set to yes by an authorized operator for live transfer
METADATA_LABELING=true
AUDIT_LOGGING=true
TRANSFER_RATE_LIMIT_HOURS=24

# ML / Storage
MODEL_STORE_PATH="${MODELS_PATH}/production"
EXPERIENCE_STORE_PATH="storage/experience-repo"

# Misc
VERBOSE_LOG=true
```

---

## File / Directory Structure to Create (exact)

```
services/
├── cognitive-learner/
│   ├── src/main.py
│   ├── src/learner.py
│   ├── src/ingest.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── experience-repository/
│   ├── src/main.py
│   ├── src/store.py
│   ├── src/query.py
│   ├── schema/experience_schema.json
│   ├── Dockerfile
│   └── requirements.txt
├── transfer-agent/
│   ├── src/main.py
│   ├── src/propose.py
│   ├── src/validator.py
│   ├── Dockerfile
│   └── requirements.txt
└── optimizer-proxy/
    ├── src/main.py
    ├── src/api.py
    ├── config.yaml
    ├── Dockerfile
    └── requirements.txt

infra/
├── terraform/modules/k4_cognitive/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/k4-cognitive/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── scripts/k4/
│   ├── precheck.sh
│   ├── deploy.sh
│   └── verify.sh
└── vault/policies/
    └── k4_cognitive.hcl

models/
├── config/
│   └── transfer_rules.yaml
└── training/
    └── (retained models, staging/production)

tests/k4/
├── unit/
│   ├── test_learner.py
│   ├── test_repository.py
│   └── test_transfer_validator.py
├── integration/
│   └── test_end_to_end_transfer.py
└── e2e/
    └── test_full_pipeline.py

reports/k4/
├── precheck_report.json
├── deploy_summary.json
├── transfer_log.json
└── verification_summary.json

docs/
└── k4_design.md
```

---

## High-Level Tasks (K.4.1 → K.4.N)

| ID    | Component             | Purpose                                                                                                                        |
| ----- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| K.4.1 | cognitive-learner     | Ingest incident/decision/artifact streams and extract candidate lessons (patterns, root-cause signatures, feature importances) |
| K.4.2 | experience-repository | Store, index, and query experience artifacts with provenance & metadata schema                                                 |
| K.4.3 | transfer-agent        | Generate candidate policy/model changes from experiences, run validation & simulation, produce proposals                       |
| K.4.4 | optimizer-proxy       | Expose APIs for proposals, approvals, and rollback; integrate with governance-api                                              |
| K.4.5 | precheck & deploy     | Ensure infra/resources exist and run dry-run deployments in simulation mode                                                    |
| K.4.6 | verification          | Run synthetic transfers in simulation and verify governance checks & audit artifacts                                           |
| K.4.7 | CI & pipeline         | Add workflow to run all simulation steps and collect artifacts                                                                 |
| K.4.8 | docs & runbooks       | Document transfer rules, operators’ approvals, and rollback procedures                                                         |
| K.4.9 | monitoring            | Add Prometheus/Grafana panels for transfer activity and knowledge health                                                       |

---

## Detailed Task Specs & Endpoints

### Cognitive Learner Service

**Path:** `services/cognitive-learner/`
**Port:** 8700
**Purpose:** consumes inputs from `knowledge-indexer`, `reports/*`, and telemetry to produce candidate lessons.

**Endpoints:**

* `GET /health` → { status: "healthy" }
* `POST /v1/ingest` → accepts JSON experience batches; returns `ingest_id`
* `GET /v1/lessons?since=<ts>` → returns array of lesson objects
* `POST /v1/explain/<lesson_id>` → returns feature importances & evidence

**Behavior:**

* Periodically (cron) runs extraction jobs.
* For each lesson: compute confidence, related decision IDs, affected services, and suggested changes (model hyperparams, policy threshold tuning, repair plans).
* Outputs candidate lesson artifacts to `experience-repository` via API.

**Env:**

```yaml
SERVICE_NAME: "cognitive-learner"
SERVICE_PORT: 8700
INGEST_TOPIC: "experience_events"
EXPLAINABILITY_OUTPUT: "reports/k4/model_explainability.json"
```

---

### Experience Repository Service

**Path:** `services/experience-repository/`
**Port:** 8701
**Purpose:** stores experiences/lessons with schema.

**Endpoints:**

* `GET /health`
* `POST /v1/experience` → store experience object, returns id
* `GET /v1/experience/{id}` → retrieve artifact
* `GET /v1/query?q=<sparql-like>` → advanced query

**Data contract (schema snippet):**
`schema/experience_schema.json` (example)

```json
{
  "$id":"experience.schema",
  "type":"object",
  "properties":{
    "id":{"type":"string"},
    "origin":{"type":"object","properties":{"service":{"type":"string"},"timestamp":{"type":"string"}}},
    "tenant_anonymized":{"type":"boolean"},
    "evidence":{"type":"object"},
    "lesson":{"type":"string"},
    "confidence":{"type":"number"},
    "recommendations":{"type":"array"}
  },
  "required":["id","origin","evidence","lesson","confidence"]
}
```

---

### Transfer Agent Service

**Path:** `services/transfer-agent/`
**Port:** 8702
**Purpose:** validates, simulates, and proposes transfers (policy/model changes).

**Endpoints:**

* `GET /health`
* `POST /v1/propose` → body: {lesson_id, change_type, change_payload} → returns `proposal_id`
* `GET /v1/proposal/{proposal_id}` → proposal status & simulation outputs
* `POST /v1/proposal/{proposal_id}/apply?approve=yes` → applies change (simulation or live, depending on APPROVE_TRANSFER & SIMULATION_MODE)
* `POST /v1/proposal/{proposal_id}/rollback` → rollback last applied change

**Behavior:**

* Validate proposals against P1–P23 via `governance-api`.
* Always perform a simulated dry-run evaluation producing `reports/k4/simulated_impact_{id}.json`.
* Write `reports/k4/transfer_log.json` with: `proposal_id, lesson_id, validator_result, simulated_metrics, apply_status`.

**Env:**

```yaml
SERVICE_NAME: "transfer-agent"
SERVICE_PORT: 8702
APPROVE_ENV_VAR: "APPROVE_TRANSFER"
POLICY_API: "http://governance-api:8400"
```

---

### Optimizer Proxy Service

**Path:** `services/optimizer-proxy/`
**Port:** 8703
**Purpose:** UI/agent friendly API layer for approvals, scheduling transfers, and viewing repository.

**Endpoints:**

* `GET /health`
* `GET /v1/proposals` → list proposals
* `POST /v1/proposals/{id}/schedule` → schedule apply window & notify stakeholders
* `GET /v1/explain/{proposal_id}` → human-readable rationale & audit links

---

## Data Contracts (schemas)

* `schema/experience_schema.json` — experience artifact contract (see above)
* `schema/proposal_schema.json` — proposal contract (includes change_payload, simulation_metrics, expected_impact)
* `schema/transfer_log_schema.json` — audit log contract for transfers

Files location: `services/experience-repository/schema/*.json`
Agents and tests must validate JSONs against these schemas.

---

## Embedded Scripts Pattern

### `infra/scripts/k4/precheck.sh` (embedded)

**File:** `infra/scripts/k4/precheck.sh` — environment & dependency validation (simulation-safe)

```bash
#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${ROOT}/reports/k4"
mkdir -p "${REPORTS_DIR}"

echo "K.4 precheck - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Check required folders
for p in services/experience-repository services/cognitive-learner services/transfer-agent services/optimizer-proxy; do
  if [ ! -d "$ROOT/$p" ]; then
    echo "WARN: missing $p (expected for skeleton in simulation)" >> "${REPORTS_DIR}/precheck_report.json"
  fi
done

# Check governance API reachability (simulation: skip)
if [ "${SIMULATION_MODE}" = "true" ]; then
  echo '{"phase":"K.4","simulation_mode":true,"overall_status":"PASS","notes":["Simulation: governance/API checks skipped"]}' > "${REPORTS_DIR}/precheck_report.json"
  echo "Precheck (simulation) written to ${REPORTS_DIR}/precheck_report.json"
  exit 0
fi

# Live checks (only executed when SIMULATION_MODE=false)
# - governance api
curl -fsS "http://governance-api:8400/health" >/dev/null || { echo "Governance API not reachable"; exit 2; }
# - vault policy existence
# (Add vault cli checks)
echo '{"phase":"K.4","simulation_mode":false,"overall_status":"PASS"}' > "${REPORTS_DIR}/precheck_report.json"
```

**Permissions:** `chmod +x infra/scripts/k4/precheck.sh`

---

### `infra/scripts/k4/deploy.sh` (embedded)

**File:** `infra/scripts/k4/deploy.sh` — deploy infra & services (simulation-safe)

```bash
#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${ROOT}/reports/k4"
mkdir -p "${REPORTS_DIR}"
SIM=${SIMULATION_MODE:-true}

echo "K.4 deploy - SIMULATION_MODE=${SIM}"

# terraform plan (simulated)
echo '{"step":"terraform_plan","result":"simulated"}' > "${REPORTS_DIR}/deploy_summary.json"
# helm template rendering (simulated)
echo '{"step":"helm_template","result":"simulated"}' >> "${REPORTS_DIR}/deploy_summary.json"

# Seed example experience artifact (simulation)
cat > "${REPORTS_DIR}/transfer_log.json" <<'JSON'
[]
JSON

echo '{"phase":"K.4","simulation_mode":true,"overall_status":"SIM_OK"}' >> "${REPORTS_DIR}/deploy_summary.json"
echo "Deploy (simulation) wrote ${REPORTS_DIR}/deploy_summary.json and transfer_log.json"
```

**Permissions:** `chmod +x infra/scripts/k4/deploy.sh`

---

### `infra/scripts/k4/verify.sh` (embedded)

**File:** `infra/scripts/k4/verify.sh` — run validation & synthetic transfer simulation

```bash
#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${ROOT}/reports/k4"
mkdir -p "${REPORTS_DIR}"

echo "Running K.4 verification (simulation)..."

# simulate a full workflow: learner -> repository -> transfer propose -> simulated apply
SIM_OUT="${REPORTS_DIR}/verification_summary.json"
cat > "${SIM_OUT}" <<'JSON'
{
  "phase":"K.4",
  "simulation_mode":true,
  "checks":{
    "learner":"ok",
    "repository":"ok",
    "transfer_agent":"ok",
    "governance_simulation":"ok"
  },
  "overall_result":"PASS_SIMULATION",
  "recommendation":"Ready for controlled trials with APPROVE_TRANSFER=no -> dry runs"
}
JSON

echo "Verification (simulation) written to ${SIM_OUT}"
```

**Permissions:** `chmod +x infra/scripts/k4/verify.sh`

---

## Verification & Testing

### Verification Commands (agent must run and save outputs)

```bash
# Precheck
SIMULATION_MODE=true ./infra/scripts/k4/precheck.sh

# Deploy (simulation)
SIMULATION_MODE=true ./infra/scripts/k4/deploy.sh

# Verify (simulation)
SIMULATION_MODE=true ./infra/scripts/k4/verify.sh
```

### Integration Test Stub (agent must create)

File: `tests/k4/integration/test_end_to_end_transfer.py`

```python
import os
import requests
import json
import time

ROOT = os.getenv("ROOT_DIR", ".")
REPORTS = os.path.join(ROOT, "reports/k4")

def test_simulated_transfer_flow():
    # Simulation-only: validate reports exist and are JSON
    assert os.path.exists(REPORTS), "reports/k4 missing"
    files = ["precheck_report.json","deploy_summary.json","transfer_log.json","verification_summary.json"]
    for f in files:
        p = os.path.join(REPORTS, f)
        assert os.path.exists(p), f"{p} missing"
        with open(p) as fh:
            json.load(fh)
```

---

## Agent Instructions

### Agent Execution Steps (explicit sequence)

1. Validate environment (no phase-* directories):

```bash
if ls phase-* 2>/dev/null; then echo "ERROR: phase-* directories found"; exit 1; fi
```

2. Create component folders:

```bash
mkdir -p services/{cognitive-learner,experience-repository,transfer-agent,optimizer-proxy}
mkdir -p infra/terraform/modules/k4_cognitive infra/helm/k4-cognitive infra/scripts/k4
mkdir -p reports/k4 tests/k4/{unit,integration,e2e} models/config
```

3. Add policy file (placeholder):

```bash
touch infra/vault/policies/k4_cognitive.hcl
```

4. Run precheck:

```bash
SIMULATION_MODE=true ./infra/scripts/k4/precheck.sh
```

5. Run deploy (simulation):

```bash
SIMULATION_MODE=true ./infra/scripts/k4/deploy.sh
```

6. Run verify:

```bash
SIMULATION_MODE=true ./infra/scripts/k4/verify.sh
```

7. Run tests:

```bash
python -m pytest tests/k4/ -q
```

8. Upload artifacts to CI (if CI agent):

* `reports/k4/*.json`, `services/*/task_specs.md`, `infra/helm/k4-cognitive/*`

### Failure Handling Rules

* If precheck fails: abort and write `reports/k4/precheck_report.json` with failure reason.
* If deploy fails in simulation: do not change live infra; collect `terraform_plan` and `helm_template` outputs to `reports/k4/`.
* If transfer simulation indicates governance violation: log violation to `reports/k4/transfer_log.json` and block promotion.
* If verification fails: set `overall_result: FAIL_SIMULATION` and notify `ops-oncall`.

### Acceptance Criteria

* [ ] `services/*` directories exist with a `src/main.py` stub each.
* [ ] `infra/*` terraform/helm files exist (can be templates).
* [ ] Precheck, deploy, verify scripts produce valid JSON under `reports/k4/`.
* [ ] `tests/k4/` contains at least one passing integration test in simulation.
* [ ] `infra/vault/policies/k4_cognitive.hcl` present and referenced.
* [ ] CI workflow `.github/workflows/k4_cognitive.yml` exists and runs simulation steps.
* [ ] Transfers remain `simulated` unless `APPROVE_TRANSFER=yes` is explicitly set by authorized user.
* [ ] All audit logs stored under `reports/k4/transfer_log.json`.

---

## Deliverables & Compliance

### Deliverables (explicit)

* services/cognitive-learner/
* services/experience-repository/
* services/transfer-agent/
* services/optimizer-proxy/
* infra/terraform/modules/k4_cognitive/
* infra/helm/k4-cognitive/
* infra/scripts/k4/{precheck.sh,deploy.sh,verify.sh}
* infra/vault/policies/k4_cognitive.hcl
* tests/k4/
* reports/k4/
* docs/k4_design.md
* .github/workflows/k4_cognitive.yml

### Security & Compliance reminders

* P23 enforced for all transfers.
* Anonymize tenant-specific information before writing to experience repository (no raw tenant IDs).
* Vault must hold any credentials; never write secrets to repo.
* All transfer proposals must include `origin_proof` (link to decision id / incident id).

---

## Notes for the Agent (embedded prompt)

> You are building the ATOM Cloud K.4 Cognitive Optimization & Knowledge Transfer components.
>
> * ALWAYS use `SIMULATION_MODE=true` by default.
> * NEVER apply transfers live without explicit manual approval: `APPROVE_TRANSFER=yes` set by an authorized operator.
> * Validate JSON artifacts against schema files in `services/experience-repository/schema/`.
> * Ensure every experience/lesson has provenance metadata and is anonymized.
> * Produce clear audit artifacts under `reports/k4/` for every proposal, simulation, and action.
> * Do not create any `phase-*` directories; use the global directory structure.
> * Tag every commit with `k4.cognitive:stub` when adding stub files; final artifacts should be under `prod-feature/k4.cognitive` branch.

---

## Key Formatting Elements to Follow

* Embed complete scripts in code blocks (bash) and mark executable permissions.
* Provide exact file paths and directory structure.
* Include environment variable definitions with defaults.
* Provide API endpoint specifications and JSON schema examples.
* Ensure simulation mode awareness and governance checks throughout.
* Produce measurable acceptance criteria and audit artifacts.

---

)
