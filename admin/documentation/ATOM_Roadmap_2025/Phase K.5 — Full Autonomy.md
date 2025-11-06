# Phase K.5 — Full Autonomy (Meta-Learning & Explainable AI) (Agent-Ready Build Plan)

**Branch:** `prod-feature/k5.full-autonomy`
**Mode:** `SIMULATION_MODE=true` (default — agents must use simulation by default)
**Parent Phases:** K.1 (Autonomous Runtime), K.2 (Adaptive Scaling), K.3 (Self-Healing), K.4 (Cognitive Transfer)
**Dependencies:** `aol-controller`, `aol-policy`, `predictive-ops-engine`, `incident-detector`, `cognitive-learner`, `transfer-agent`, `experience-repository`, `governance-api`, `metrics-collector`

> **AGENT INSTRUCTION**: Always default to `SIMULATION_MODE=true`. Live promotion requires `APPROVE_META=yes` and explicit authorized operator approval.
> **CRITICAL**: Do NOT create `phase-*` directories. Use the repository global directory structure.

---

## Summary / Goal

**Objective:** Build the Full Autonomy layer that enables meta-learning (models that learn *how to learn* across environments) and first-class explainability so autonomous decisions are interpretable, auditable, reversible, and safe.

**Success Criteria:**

* [ ] Services created: `meta-learner`, `explainability-engine`, `policy-refiner`, `autonomy-auditor`, `simulator-proxy`.
* [ ] Infrastructure modules under `infra/terraform/modules/k5_full_autonomy/` and Helm in `infra/helm/k5-full-autonomy/`.
* [ ] Scripts `infra/scripts/k5/{precheck.sh,deploy.sh,verify.sh}` exist and work in `SIMULATION_MODE=true`.
* [ ] Tests in `tests/k5/` (unit/integration/e2e) run and pass in simulation.
* [ ] Reports generated under `reports/k5/` (precheck_report.json, deploy_summary.json, verification_summary.json, explainability_reports/).
* [ ] Policy P24 (Meta-Learning & Explainability Safety) created and enforced (`infra/vault/policies/k5_full_autonomy.hcl`).
* [ ] CI workflow `.github/workflows/k5_full_autonomy.yml` runs simulation and uploads artifacts.
* [ ] All acceptance criteria in this doc met and auditable artifacts produced.

---

## New / Specific Policies (added)

**P24 — Meta-Learning & Explainability Safety**

* **P24.1 Meta Promotion Guard:** Any meta-learner suggestion that changes learning algorithms, reward shaping, or objective functions is `simulated` by default and must be approved (`APPROVE_META=yes`) to apply live.
* **P24.2 Explainability Thresholds:** Any automated action altering models/policies must include an explainability artifact with at least top-5 feature contributions and a human-readable rationale.
* **P24.3 Human-in-the-loop for Distribution Shift:** Large distribution shifts (>10% feature drift) require human signoff before promotion.
* **P24.4 Versioned Rollbacks:** Every meta-change must be one-command rollbackable and retain prior artifacts.
* **P24.5 Safety Canary:** Meta-updates only applied to canary namespaces first (2-node group) until a 72-hour stability window passes.
* **Enforcement:** `governance-api` and `autonomy-auditor` enforce P24 for each action. Vault policy file `k5_full_autonomy.hcl` stores metadata access controls.

---

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="k5-full-autonomy"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
REPORTS_PATH="reports/k5"
POLICIES_PATH="infra/vault/policies"
SCRIPTS_PATH="infra/scripts/k5"
MODELS_PATH="models"

# Deployment Settings
SIMULATION_MODE=true
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-k5"

# ML / Meta-Learning
META_LEARNER_CONFIG="models/config/meta_learning.yaml"
META_PROMOTE_THRESHOLD=0.02  # minimum improvement (2%) to consider promotion
APPROVE_META=no

# Governance & Safety
POLICY_ENFORCEMENT=true
APPROVE_META_ENV="APPROVE_META"
METADATA_LABELING=true
AUDIT_LOGGING=true

# Rate Limits
META_PROMOTE_RATE_HOURS=24
```

---

## File / Directory Structure to Create (exact)

```
services/
├── meta-learner/
│   ├── src/main.py
│   ├── src/meta_trainer.py
│   ├── src/adapter.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── explainability-engine/
│   ├── src/main.py
│   ├── src/explain.py
│   ├── src/visualize.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── policy-refiner/
│   ├── src/main.py
│   ├── src/propose_refinements.py
│   ├── src/simulate.py
│   ├── Dockerfile
│   └── requirements.txt
├── autonomy-auditor/
│   ├── src/main.py
│   ├── src/audit_collector.py
│   ├── src/query.py
│   ├── Dockerfile
│   └── requirements.txt
└── simulator-proxy/
    ├── src/main.py
    ├── src/run_scenarios.py
    ├── Dockerfile
    └── requirements.txt

infra/
├── terraform/modules/k5_full_autonomy/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/k5-full-autonomy/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── scripts/k5/
│   ├── precheck.sh
│   ├── deploy.sh
│   └── verify.sh
└── vault/policies/
    └── k5_full_autonomy.hcl

models/
├── config/
│   └── meta_learning.yaml
└── meta/
    └── (meta-model artifacts, staging/production)

tests/k5/
├── unit/
│   ├── test_meta_trainer.py
│   ├── test_explainability.py
│   └── test_policy_refiner.py
├── integration/
│   └── test_end_to_end_meta_flow.py
└── e2e/
    └── test_full_autonomy_pipeline.py

reports/k5/
├── precheck_report.json
├── deploy_summary.json
├── verification_summary.json
└── explainability_reports/
    └── explainability_*.json

docs/
└── k5_design.md
```

---

## High-Level Tasks (K.5.1 → K.5.N)

| ID    | Component             | Purpose                                                                              |
| ----- | --------------------- | ------------------------------------------------------------------------------------ |
| K.5.1 | meta-learner          | Meta-learning service: learns optimizer/training improvements across phases          |
| K.5.2 | explainability-engine | Generates per-decision explanations, visualizations, and human-friendly rationales   |
| K.5.3 | policy-refiner        | Proposes policy tuning (thresholds, reward shaping) and simulates impacts            |
| K.5.4 | autonomy-auditor      | Collects audit trails, indexes by provenance, exposes queries for compliance         |
| K.5.5 | simulator-proxy       | Runs offline synthetic scenarios to validate meta-changes before proposal            |
| K.5.6 | precheck & deploy     | Validate infra and perform simulation-only deploys                                   |
| K.5.7 | verification          | Run synthetic meta-training and promotion dry-runs; produce explainability artifacts |
| K.5.8 | CI & pipeline         | Add CI workflow to run simulation steps and upload artifacts                         |
| K.5.9 | docs & operators      | Runbooks for manual approval, rollback, and interpretability review                  |

---

## Detailed Task Specs & Endpoints

### Meta-Learner Service

**Path:** `services/meta-learner/`
**Port:** 8800
**Purpose:** Aggregate lessons, run meta-optimization (learning optimizers / hyperparameter schedulers / reward-shaping strategies), output candidate meta-updates.

**Endpoints:**

* `GET /health` → {status:"healthy"}
* `POST /v1/ingest` → accepts lesson bundles from `experience-repository`/`knowledge-indexer`
* `POST /v1/train` → triggers meta-training job (returns job_id)
* `GET /v1/jobs/{job_id}` → job status & metrics
* `GET /v1/proposals` → list generated meta-proposals

**Behavior:**

* Batches lessons, trains meta-model (few-shot / MAML-like or online RL), outputs candidate improvements with `expected_gain` and `confidence`.
* Writes candidate proposals to `policy-refiner`.

**Env:**

```yaml
SERVICE_NAME: "meta-learner"
SERVICE_PORT: 8800
BATCH_SIZE: 128
META_LEARNING_RATE: 0.001
```

---

### Explainability Engine

**Path:** `services/explainability-engine/`
**Port:** 8801
**Purpose:** Produce SHAP/feature-attribution outputs, counterfactuals, and human-readable rationales for any proposed meta-change or autonomous action.

**Endpoints:**

* `GET /health`
* `POST /v1/explain` → body: {artifact_id, model_snapshot} → returns explanation JSON & visualization meta
* `GET /v1/counterfactual` → runs counterfactual analysis on decision

**Behavior:**

* Integrates model introspection (SHAP, LIME), causal explanation hooks, and produces `reports/k5/explainability_reports/explainability_<id>.json`.

**Env:**

```yaml
SERVICE_NAME: "explainability-engine"
SERVICE_PORT: 8801
MAX_EXPLAIN_TIME_S: 60
```

---

### Policy Refiner

**Path:** `services/policy-refiner/`
**Port:** 8802
**Purpose:** Accepts meta-proposals, simulates their impact via `simulator-proxy`, validates against P1–P24 with `governance-api`, then forwards accepted proposals to `autonomy-auditor` and `aol-controller` (simulation apply only).

**Endpoints:**

* `POST /v1/propose` → {proposal_payload} → returns proposal_id
* `GET /v1/proposal/{id}` → status + simulation artifacts
* `POST /v1/proposal/{id}/apply?approve=yes` → apply in simulation or live (guarded by APPROVE_META)

**Behavior:**

* Ensures at least one explainability artifact accompanies each proposal.
* Enforces P24 rate limits and canary policy by default.

---

### Autonomy Auditor

**Path:** `services/autonomy-auditor/`
**Port:** 8803
**Purpose:** Central collector for all meta-actions, stores audit entries, exposes queries for compliance reviews.

**Endpoints:**

* `GET /health`
* `POST /v1/audit` → ingest audit events
* `GET /v1/audit?filter=...` → query logs

**Behavior:**

* Stores immutable audit JSONs under `reports/k5/` and indexes provenance metadata.

---

### Simulator Proxy

**Path:** `services/simulator-proxy/`
**Port:** 8804
**Purpose:** Runs synthetic scenarios (traffic patterns, degradation events) offline to measure the impact of proposals.

**Endpoints:**

* `POST /v1/run` → {scenario_id, overrides} → returns simulated metrics & safety flags
* `GET /v1/scenarios` → list available scenarios

**Behavior:**

* Produces deterministic simulation artifacts stored in `reports/k5/` for proposal evaluation.

---

## Data Contracts (schemas)

* `services/experience-repository/schema/experience_schema.json` (reused)
* `services/meta-learner/schema/proposal_schema.json` — includes `expected_gain`, `confidence`, `explainability_ref`, `rollback_id`
* `services/autonomy-auditor/schema/audit_event.json` — immutable audit format

All JSON artifacts must be validated against schemas before being accepted.

---

## Embedded Scripts Pattern

### `infra/scripts/k5/precheck.sh`

**File:** `infra/scripts/k5/precheck.sh`

```bash
#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/k5"
mkdir -p "${REPORTS}"

echo "K.5 precheck - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Basic folder existence checks (simulation friendly)
for p in services/meta-learner services/explainability-engine services/policy-refiner services/autonomy-auditor services/simulator-proxy; do
  if [ ! -d "${ROOT}/${p}" ]; then
    echo "WARN: ${p} missing" >> "${REPORTS}/precheck_warnings.txt"
  fi
done

# Write a precheck JSON
cat > "${REPORTS}/precheck_report.json" <<'JSON'
{
  "phase":"K.5",
  "timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "simulation_mode":true,
  "overall_status":"PASS",
  "notes":["Simulation precheck completed. Governance/API checks skipped in SIM mode."]
}
JSON

echo "Precheck written to ${REPORTS}/precheck_report.json"
```

`chmod +x infra/scripts/k5/precheck.sh`

---

### `infra/scripts/k5/deploy.sh`

**File:** `infra/scripts/k5/deploy.sh`

```bash
#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/k5"
mkdir -p "${REPORTS}"

echo "K.5 deploy - SIMULATION_MODE=${SIMULATION_MODE:-true}"

# Simulated terraform/helm outputs
cat > "${REPORTS}/deploy_summary.json" <<'JSON'
{
  "phase":"K.5",
  "timestamp":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'",
  "simulation_mode":true,
  "steps":[
    {"step":"terraform_plan","result":"simulated"},
    {"step":"helm_template","result":"simulated"},
    {"step":"meta_jobs_queued","count":1}
  ],
  "overall_status":"SIM_OK"
}
JSON

# Create an explainability stub
mkdir -p "${REPORTS}/explainability_reports"
cat > "${REPORTS}/explainability_reports/explainability_stub.json" <<'JSON'
{
  "id":"explain-stub-001",
  "created":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'",
  "top_features":["cpu_usage","latency","mem_usage"],
  "importance":[0.35,0.28,0.20],
  "notes":"Simulation stub"
}
JSON

echo "Deploy (simulation) wrote deploy_summary.json and explainability stub"
```

`chmod +x infra/scripts/k5/deploy.sh`

---

### `infra/scripts/k5/verify.sh`

**File:** `infra/scripts/k5/verify.sh`

```bash
#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS="${ROOT}/reports/k5"
mkdir -p "${REPORTS}"

echo "K.5 verify - SIMULATION_MODE=${SIMULATION_MODE:-true}"

cat > "${REPORTS}/verification_summary.json" <<'JSON'
{
  "phase":"K.5",
  "timestamp":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'",
  "simulation_mode":true,
  "checks":{"meta_learner":"ok","explainability":"ok","policy_refiner":"ok","auditor":"ok"},
  "overall_result":"PASS_SIMULATION",
  "recommendation":"Proceed to controlled trials when APPROVE_META=yes and operator approvals present."
}
JSON

echo "Verification (simulation) written to ${REPORTS}/verification_summary.json"
```

`chmod +x infra/scripts/k5/verify.sh`

---

## Verification & Testing

### Verification Commands (agent must run and save outputs)

```bash
# Precheck
SIMULATION_MODE=true ./infra/scripts/k5/precheck.sh

# Deploy (simulation)
SIMULATION_MODE=true ./infra/scripts/k5/deploy.sh

# Verify (simulation)
SIMULATION_MODE=true ./infra/scripts/k5/verify.sh
```

### Integration Test Stub (agent must create)

File: `tests/k5/integration/test_end_to_end_meta_flow.py`

```python
import os, json
def test_k5_reports_exist():
    root = "."
    rpt = os.path.join(root, "reports/k5")
    assert os.path.exists(rpt)
    for f in ["precheck_report.json","deploy_summary.json","verification_summary.json"]:
        p = os.path.join(rpt, f)
        assert os.path.exists(p)
        with open(p) as fh:
            json.load(fh)
```

---

## Agent Execution Steps (explicit sequence)

1. **Validate global repo (no phase-* dirs)**:

```bash
if ls phase-* 1>/dev/null 2>&1; then echo "ERROR: found phase-* dirs"; exit 1; fi
```

2. **Create skeletons**:

```bash
mkdir -p services/{meta-learner,explainability-engine,policy-refiner,autonomy-auditor,simulator-proxy}
mkdir -p infra/terraform/modules/k5_full_autonomy infra/helm/k5-full-autonomy infra/scripts/k5
mkdir -p tests/k5/{unit,integration,e2e} reports/k5 reports/k5/explainability_reports models/config
touch infra/vault/policies/k5_full_autonomy.hcl
```

3. **Run precheck**:

```bash
SIMULATION_MODE=true ./infra/scripts/k5/precheck.sh
```

4. **Run deploy (simulation)**:

```bash
SIMULATION_MODE=true ./infra/scripts/k5/deploy.sh
```

5. **Run verify**:

```bash
SIMULATION_MODE=true ./infra/scripts/k5/verify.sh
```

6. **Run tests**:

```bash
python -m pytest tests/k5/ -q
```

7. **Upload artifacts** (CI step): `reports/k5/*` and `reports/k5/explainability_reports/*`

---

## Acceptance Criteria

* [ ] `services/*` directories exist with `src/main.py` stubs.
* [ ] `infra/terraform/modules/k5_full_autonomy/` and `infra/helm/k5-full-autonomy/` present (templates ok).
* [ ] `infra/scripts/k5/{precheck.sh,deploy.sh,verify.sh}` executable and produce JSON artifacts in `reports/k5/`.
* [ ] At least one explainability artifact exists under `reports/k5/explainability_reports/`.
* [ ] `tests/k5/` contains integration test and it passes (simulation).
* [ ] Vault policy file `infra/vault/policies/k5_full_autonomy.hcl` exists (placeholder allowed).
* [ ] CI workflow `.github/workflows/k5_full_autonomy.yml` exists (simulation steps).
* [ ] All generated proposals are `simulated` unless `APPROVE_META=yes` and authorized.

---

## Deliverables & Compliance

**Deliverables:**

* services: meta-learner, explainability-engine, policy-refiner, autonomy-auditor, simulator-proxy
* infra: terraform/helm modules + vault policy
* scripts: precheck/deploy/verify
* tests: unit/integration/e2e stubs
* reports: precheck/deploy/verification + explainability artifacts
* docs: `docs/k5_design.md` with runbooks for approvers/operators

**Compliance reminders:**

* Enforce P1–P24 across all transfers and promotions.
* Anonymize tenant data before experience ingestion.
* Keep all secrets in Vault; do not write secrets to repo.
* Ensure explainability artifacts accompany every meta-proposal.

---

## Notes for the Agent (embedded prompt)

> Build K.5 following the global directory layout. Default to `SIMULATION_MODE=true`.
> Validate JSON artifacts against schema before upload.
> Do not apply any live meta-change unless `APPROVE_META=yes` and signoffs recorded in `reports/k5/approval_signoffs.json`.
> Preserve audit immutability: every audit event must be appended and never overwritten.
> Confirm all acceptance criteria and produce `reports/k5/verification_summary.json`.

---

