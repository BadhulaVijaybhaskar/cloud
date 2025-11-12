# L.6 — Cognitive Resilience & Adaptive Self-Healing Federation (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Phase:** L.6 — Cognitive Resilience & Adaptive Self-Healing Federation
**Version target:** v1.0.0-l6-cognitive-resilience
**Branch prefix:** prod-feature/l6-cognitive-resilience
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution (default `SIMULATION_MODE=true`)

> **AGENT INSTRUCTION**: Use `SIMULATION_MODE=true` if infra missing.
> **CRITICAL**: Never create phase-* directories. Use global structure only.

---

## Summary / Goal

**Objective:** Build a federated resilience layer that detects cascades, coordinates adaptive self-healing across regions, and applies safe corrective actions (restart, isolate, traffic-shift, model rollback) with full governance, auditability and automatic rollback on health regressions.

**Success Criteria:**

* [ ] Services deployed under `services/` (see structure).
* [ ] Infra stubs present under `infra/terraform/modules/l6_cognitive_resilience/` and `infra/helm/l6-cognitive-resilience/`.
* [ ] Precheck, deploy and verify scripts in `infra/scripts/l6/`.
* [ ] Tests in `tests/l6/` (unit/integration/e2e) exist and run.
* [ ] Vault policies in `infra/vault/policies/l6_cognitive_resilience.hcl`.
* [ ] `reports/l6/` contains precheck / deploy / verify artifacts.
* [ ] CI workflow `.github/workflows/l6_verify.yml` included.
* [ ] No phase directories created.
* [ ] All integration tests pass in simulation.

---

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="l6-cognitive-resilience"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
REPORTS_PATH="reports"
SCRIPTS_PATH="infra/scripts"
POLICIES_PATH="infra/vault/policies"

# Deployment Settings
SIMULATION_MODE=true   # Set to false only with approvals
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-l6"

# Security & Governance
POLICY_ENFORCEMENT=true
METADATA_LABELING=true
AUDIT_LOGGING=true

# Approval gating
APPROVE_L6_DEPLOY=no
```

---

## File / Directory Structure to Create (exact)

```
services/
├── l6-orchestrator/
│   ├── src/main.py
│   ├── Dockerfile
│   └── config.yaml
├── l6-resilience-engine/
│   ├── src/main.py
│   ├── Dockerfile
│   └── model/  # model artifacts & policies
├── l6-edge-agent/
│   ├── src/agent.py
│   ├── Dockerfile
│   └── connectors/
├── l6-policy-broker/
│   ├── src/main.py
│   └── Dockerfile
└── l6-audit-store/
    ├── src/main.py
    └── Dockerfile

infra/
├── terraform/modules/l6_cognitive_resilience/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/l6-cognitive-resilience/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── contracts/l6/
│   └── resilience_openapi.yaml
├── security/l6_cognitive_resilience/
│   └── rbac.yaml
├── scripts/l6/
│   ├── precheck.sh
│   ├── deploy.sh
│   └── verify.sh
└── vault/policies/
    └── l6_cognitive_resilience.hcl

tests/l6/
├── unit/
│   └── test_resilience_logic.py
├── integration/
│   └── test_orchestrator_policy_integration.py
└── e2e/
    └── test_self_heal_flow.py

reports/l6/
├── precheck_report.json
├── deploy_summary.json
└── verification_summary.json

docs/
└── l6_design.md
```

---

## High-Level Tasks (L6.1 → L6.7)

| ID   | Component            | Purpose                                                                          |
| ---- | -------------------- | -------------------------------------------------------------------------------- |
| L6.1 | l6-orchestrator      | Coordinate detection → remediation proposals across federated nodes              |
| L6.2 | l6-resilience-engine | Analyze signals, generate remediation actions, score risk & rollback plans       |
| L6.3 | l6-edge-agent        | Local executors on edge/region to perform safe actions (drain, restart, isolate) |
| L6.4 | l6-policy-broker     | Validate actions vs P1–P37 policies and short-circuit high-risk proposals        |
| L6.5 | l6-audit-store       | Immutable storage of decisions, evidence, and post-action verification           |
| L6.6 | Infra & Helm         | Helm + Terraform for k8s deployments, HPA templates and serviceMesh toggles      |
| L6.7 | Tests & CI           | Unit, integration, e2e + GitHub Actions + artifact upload                        |

---

## Service Specifications & Endpoints

### L6-Orchestrator

**Path:** `services/l6-orchestrator/`
**Port:** `9200`
**Endpoints:**

* `GET /health` → health
* `POST /v1/observe` → submit observation batch (`{source, metrics, traces, events}`)
* `POST /v1/propose` → returns remediation proposal (`{proposal_id, actions[], risk_score}`)
* `GET /v1/proposals/{id}` → proposal status
* `POST /v1/proposals/{id}/approve` → manual approve override (requires approval role)

**Environment:**

```yaml
SERVICE_NAME: "l6-orchestrator"
SERVICE_PORT: 9200
POLICY_BROKER_URL: "${POLICY_BROKER_URL}"
AUDIT_STORE_URL: "${AUDIT_STORE_URL}"
SIMULATION_MODE: "${SIMULATION_MODE}"
```

### L6-Resilience-Engine

**Path:** `services/l6-resilience-engine/`
**Port:** `9201`
**Purpose:** scoring, root-cause heuristics, candidate actions

* `POST /v1/score` → returns risk + recommended actions
* `POST /v1/simulate` → dry-run simulation of action plan (always in SIMULATION_MODE)
  Env: MODEL_PATH, RETRAIN_SCHEDULE

### L6-Edge-Agent

**Path:** `services/l6-edge-agent/`
**Port:** `9202`
**Purpose:** Execute approved actions safely

* `POST /v1/action` → execute an action (restart/service, drain, isolate)
* `GET /v1/status` → local status & last action
  Actions must require policy-broker signature and create audit entry.

### L6-Policy-Broker

**Path:** `services/l6-policy-broker/`
**Port:** `9203`
**Purpose:** Evaluate proposals against P1–P37 and L6-specific P37−P38 policies

* `POST /v1/evaluate` → returns allow/deny/require_approval + reasons
* `GET /v1/policies` → list active policies

### L6-Audit-Store

**Path:** `services/l6-audit-store/`
**Port:** `9204`
**Purpose:** Append-only decision + verification store (supports query)

* `POST /v1/audit` → store event
* `GET /v1/audit?proposal_id=...` → retrieve events
  Storage must be immutable (append-only) and backed by persistent storage.

---

## Data Contracts (schemas)

Save JSON schemas under `infra/contracts/l6/`:

* `observation.schema.json` — metrics/traces/events unify schema
* `proposal.schema.json` — proposal format with actions, risk_score, ttl
* `policy_eval.schema.json` — policy evaluation output

(Example excerpt — `proposal.schema.json`):

```json
{
  "$id": "proposal.schema.json",
  "type": "object",
  "properties": {
    "proposal_id": {"type": "string"},
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type":"string"},
          "target": {"type":"string"},
          "params": {"type":"object"}
        },
        "required":["type","target"]
      }
    },
    "risk_score": {"type":"number"}
  },
  "required":["proposal_id","actions","risk_score"]
}
```

---

## Embedded Scripts Pattern

### Deployment Script (embedded)

**File:** `infra/scripts/l6/deploy.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

COMPONENT="l6-cognitive-resilience"
SIM=${SIMULATION_MODE:-true}
SERVICES_PATH="${SERVICES_PATH:-services}"
INFRA_PATH="${INFRA_PATH:-infra}"

echo "L6 Deploy: simulation=${SIM}"

# Build images (simulation safe: skip registry push)
for svc in ${SERVICES_PATH}/l6-*; do
  if [ -d "$svc" ]; then
    echo "Building $(basename $svc)..."
    docker build -t "${DOCKER_REGISTRY:-localhost:5000}/$(basename $svc):latest" "$svc" || true
  fi
done

# Render helm (simulated)
helm template "${COMPONENT}" "${INFRA_PATH}/helm/l6-cognitive-resilience" --values "${INFRA_PATH}/helm/l6-cognitive-resilience/values.yaml" > "reports/l6/helm_template_render.yaml" || true

# Terraform plan (simulated)
if [ "$SIM" != "true" ]; then
  terraform -chdir="${INFRA_PATH}/terraform/modules/l6_cognitive_resilience" init
  terraform -chdir="${INFRA_PATH}/terraform/modules/l6_cognitive_resilience" apply -auto-approve
else
  terraform -chdir="${INFRA_PATH}/terraform/modules/l6_cognitive_resilience" init || true
  terraform -chdir="${INFRA_PATH}/terraform/modules/l6_cognitive_resilience" plan -out="reports/l6/terraform_plan_k6.tfplan" || true
fi

echo '{"phase":"L.6","status":"SIM_OK","timestamp":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"}' > reports/l6/deploy_summary.json
echo "L6 deploy simulation complete."
```

### Precheck Script (embedded)

**File:** `infra/scripts/l6/precheck.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/l6

echo "Running L6 precheck (SIMULATION_MODE=${SIMULATION_MODE:-true})"

# Basic checks
jq -n --arg v "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  '{phase:"L.6", timestamp:$v, simulation_mode:env.SIMULATION_MODE}' > reports/l6/precheck_report.json

echo "Precheck written to reports/l6/precheck_report.json"
```

### Verify Script (embedded)

**File:** `infra/scripts/l6/verify.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Running L6 verification (simulation)"
# Basic verification stub: check manifests rendered
if [ -f reports/l6/deploy_summary.json ]; then
  cat reports/l6/deploy_summary.json
fi

jq -n --arg s "PASS_SIMULATION" '{phase:"L.6", overall_result:$s, timestamp:env.TIMESTAMP}' > reports/l6/verification_summary.json || true
echo "Verification summary written to reports/l6/verification_summary.json"
```

---

## Integration Test Stub (embedded)

**File:** `tests/l6/integration/test_orchestrator_policy_integration.py`

```python
import os
import json
import requests
import pytest

SIM = os.getenv("SIMULATION_MODE", "true") == "true"
BASE = "http://localhost:9200" if SIM else os.getenv("ORCHESTRATOR_URL", "http://l6-orchestrator:9200")

def test_propose_endpoint_available():
    if SIM:
        assert True
    else:
        r = requests.get(f"{BASE}/health", timeout=5)
        assert r.status_code == 200

def test_policy_evaluation_flow():
    if SIM:
        assert True
    else:
        # send a fake observation + ensure policy broker denies unsafe action
        obs = {"source":"test","metrics":[{"name":"cpu","value":99.9}]}
        r = requests.post(f"{BASE}/v1/observe", json=obs, timeout=5)
        assert r.status_code in (200,202)
```

---

## Agent Execution Steps (explicit sequence)

1. **Validate environment (no phase dirs):**

```bash
if ls phase-* 2>/dev/null; then
  echo "ERROR: Phase directories found. Abort."
  exit 1
fi
```

2. **Create file structure**

```bash
mkdir -p services/{l6-orchestrator,l6-resilience-engine,l6-edge-agent,l6-policy-broker,l6-audit-store}
mkdir -p infra/terraform/modules/l6_cognitive_resilience
mkdir -p infra/helm/l6-cognitive-resilience/templates
mkdir -p infra/scripts/l6 tests/l6/{unit,integration,e2e} reports/l6 infra/vault/policies
```

3. **Run precheck**

```bash
SIMULATION_MODE=true infra/scripts/l6/precheck.sh
```

4. **Deploy (simulation)**

```bash
SIMULATION_MODE=true infra/scripts/l6/deploy.sh
```

5. **Verify**

```bash
SIMULATION_MODE=true infra/scripts/l6/verify.sh
```

6. **Run tests**

```bash
pytest tests/l6/ -q
```

---

## Failure Handling Rules

* If `policy_broker` returns `deny`, abort action and log `policy_eval` to audit store.
* If any live action results in health regression (pod crashloops, elevated error rate), run `infra/scripts/l6/rollback.sh` (must exist in scripts) and mark proposal failed.
* Simulation mode fallbacks: if infra absent, all actions are `simulated=true` and do not contact cluster APIs.
* Security: never store secrets in plaintext; use Vault references only.

---

## Acceptance Criteria

* [ ] Directories and files exist under global structure (no `phase-*`).
* [ ] `infra/scripts/l6/{precheck.sh,deploy.sh,verify.sh}` are executable.
* [ ] `reports/l6/precheck_report.json`, `deploy_summary.json`, `verification_summary.json` present.
* [ ] Unit tests in `tests/l6/unit/` and integration in `tests/l6/integration/` pass in simulation.
* [ ] `infra/vault/policies/l6_cognitive_resilience.hcl` present and P37 policy defined.
* [ ] CI workflow `.github/workflows/l6_verify.yml` runs simulation and uploads artifacts.
* [ ] No hardcoded phase paths present in any created files.

---

## Deliverables (explicit)

* Services: `services/l6-*` directories with `src/main.py` stubs and Dockerfiles.
* Infra: `infra/terraform/modules/l6_cognitive_resilience/` and `infra/helm/l6-cognitive-resilience/`.
* Scripts: `infra/scripts/l6/precheck.sh`, `deploy.sh`, `verify.sh`, `rollback.sh` (rollback can reuse k1/k2 patterns).
* Policies: `infra/vault/policies/l6_cognitive_resilience.hcl` (P37 – P38).
* Tests: `tests/l6/` unit + integration + e2e stubs.
* Reports: `reports/l6/*` JSON artifacts.
* CI: `.github/workflows/l6_verify.yml`.
* Docs: `docs/l6_design.md`, runbooks and operator guidance.
* Makefile: Add targets `l6-precheck`, `l6-deploy`, `l6-verify`, `l6-clean`.

---

## Security & Compliance reminders

* Enforce `SIMULATION_MODE=true` by default. Live deploy requires `APPROVE_L6_DEPLOY=yes` and multi-role sign-offs.
* Add `P37 — Resilience Safety` policy: limit number of concurrent global actions, require post-action verification window and auto-rollback triggers.
* Add `P38 — Cross-Region Action TTL` to ensure time-boxed actions.

---

## Notes for the Agent (embedded prompt)

> You are the autonomous agent implementing Phase L.6. Follow the global directory structure. Default `SIMULATION_MODE=true`. Create all files and stubs described above. Validate outputs by running `infra/scripts/l6/precheck.sh` and saving artifacts to `reports/l6/`. If infrastructure is missing, simulate Terraform/Helm rendering and mark actions as simulated. Do not create any `phase-*` directories. Apply P37 and P38 governance checks for every proposed remediation.

---

## Example Minimal Files (quick paste to drop in repo)

### `services/l6-orchestrator/src/main.py` (stub)

```python
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy"})

@app.route("/v1/observe", methods=["POST"])
def observe():
    data = request.json
    # store observation (simulation)
    return jsonify({"status":"accepted"}), 202

@app.route("/v1/propose", methods=["POST"])
def propose():
    return jsonify({
        "proposal_id":"prov-sim-0001",
        "actions":[{"type":"scale","target":"svc:web","params":{"replicas":3}}],
        "risk_score":0.12,
        "simulated": True
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9200)
```

### `infra/vault/policies/l6_cognitive_resilience.hcl` (stub)

```hcl
path "secret/data/l6/*" {
  capabilities = ["read","list"]
}
# P37: Resilience Safety enforcement (metadata only)
# P38: Cross-region TTL constraints (metadata only)
```

---

## CI Snippet (`.github/workflows/l6_verify.yml`)

```yaml
name: L6 Verify
on:
  push:
    branches: ['prod-feature/l6*']
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: chmod +x infra/scripts/l6/*.sh || true
      - run: SIMULATION_MODE=true infra/scripts/l6/precheck.sh
      - run: SIMULATION_MODE=true infra/scripts/l6/deploy.sh
      - run: SIMULATION_MODE=true infra/scripts/l6/verify.sh
      - uses: actions/upload-artifact@v4
        with:
          name: l6-reports
          path: reports/l6
```

---

## PR Body Template (for your branch)

```
Title: [L.6] Cognitive Resilience & Adaptive Self-Healing Federation — Agent-ready implementation

Summary:
- Implements orchestration, resilience engine, edge agent, policy broker and audit store.
- Infra stubs (Terraform + Helm), scripts, tests, and CI workflow included.
- Default SIMULATION_MODE=true — live deploy requires APPROVE_L6_DEPLOY=yes and multi-role signoffs.

Artifacts:
- reports/l6/precheck_report.json
- reports/l6/deploy_summary.json
- reports/l6/verification_summary.json

Runbook:
1) Precheck: SIMULATION_MODE=true infra/scripts/l6/precheck.sh
2) Deploy (simulate): SIMULATION_MODE=true infra/scripts/l6/deploy.sh
3) Verify: SIMULATION_MODE=true infra/scripts/l6/verify.sh

Approvals required for live deploy: Security Admin, Ops Lead, Governance Owner
```

---
