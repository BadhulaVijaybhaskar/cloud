Phase I.1 — Global Intelligence Fabric agent-ready file and SVG. Paste the markdown verbatim to `/docs/Phase_I.1_Global_Intelligence_Fabric_Agent.md` and the SVG verbatim to `infra/diagrams/Phase_I.1_Architecture.svg`. The agent can run them directly.

```markdown
# Phase I.1 — Global Intelligence Fabric (Agent-Ready .md)

**Objective**  
Unify regional Neural Fabrics, Quantum Agents, Federation, and Governance into a continuously-learning Global Intelligence Fabric. Provide secure distributed learning, federated model updates, global feature store coordination, cross-region inference routing, and closed-loop policy feedback.

**Version:** v9.0.0-phaseI.1  
**Branch prefix (local):** `prod-feature/I.1.<task>`  
**Mode:** Autonomous with `SIMULATION_MODE` fallback

---

## Environment variables (agent must read)

```

GLOBAL_REGISTRY_URL
POSTGRES_DSN
POSTGRES_REPLICA_DSNS
VAULT_ADDR
COSIGN_KEY_PATH
PROM_URL
NEURAL_FABRIC_URL
QUANTUM_COORD_URL
FEDERATION_TOKEN
SIMULATION_MODE
GLOBAL_S3_ENDPOINT
MODEL_STORE_URL
RULES_ENGINE_URL
REPL_WINDOW_MS

```

If any critical var missing set `SIMULATION_MODE=true` and record in precheck.

---

## Policies enforced (inherit P1–P7)

- P1 Data Privacy: Federated learning only on consented/aggregated features. No raw PII crossing regions unless approved.
- P2 Secrets & Signing: All model package exchanges and policy updates must be cosign-signed.
- P3 Execution Safety: Any autonomous global action > threshold requires approver. Dry-run default.
- P4 Observability: `/health` and `/metrics` on every service. Global tracer span id injected.
- P5 Multi-Tenancy: Tenant-scoped model namespaces, RLS enforcement.
- P6 Performance Budget: p95 routing < 500ms intra-region, < 1s inter-region for inference traffic.
- P7 Resilience & Recovery: Snapshot + verifiable rollback for models and policies.

---

## High-level tasks (I.1.1 → I.1.6)

| ID | Task | Goal |
|---:|------|------|
| I.1.1 | Global Feature Catalog | Federated feature store meta + discovery |
| I.1.2 | Federated Trainer Orchestrator | Schedule secure federated training rounds |
| I.1.3 | Model Exchange Bus | Signed model package exchange + versioning |
| I.1.4 | Global Inference Router | Policy-aware routing to best region/runtime |
| I.1.5 | Continuous Policy Feedback Loop | Policy updates from governance → fabric |
| I.1.6 | Fabric Scorecard & Auto-tuner | Metrics-driven model tuning and rollout gating |

---

## Files & dirs to create (exact list)

```

services/global-feature-catalog/
services/federated-trainer/
services/model-exchange-bus/
services/global-inference-router/
services/policy-feedback-loop/
services/fabric-scorecard/
infra/diagrams/Phase_I.1_Architecture.svg
infra/sql/i1_migrations.sql
tests/integration/test_I.1_end2end.py
docs/policies/global_intel_policy.md
reports/

```

Each service must include `main.py`, `requirements.txt`, `Dockerfile`, `config.example.yaml`, `tests/` and expose `/health` and `/metrics`.

---

## Task details (abbreviated — agent implements full stubs)

### I.1.1 — Global Feature Catalog
**Branch:** `prod-feature/I.1.1-feature-catalog`  
**Files**
```

services/global-feature-catalog/main.py
services/global-feature-catalog/catalog.py
services/global-feature-catalog/tests/test_catalog.py
reports/I.1.1_feature_catalog.md

```
**Endpoints**
- `POST /features/register` {tenant, feature_id, schema, fingerprint, consented}
- `GET /features/{tenant}` list features
- `GET /health` `GET /metrics`
**Behavior**
- Validate tenant JWT (P5).
- Ensure feature fingerprints hashed (sha256) and consent flags recorded.
**Verification**
```

pytest -q services/global-feature-catalog/tests/test_catalog.py > /reports/logs/I.1.1.log 2>&1 || true
curl -s -X POST [http://localhost:9001/features/register](http://localhost:9001/features/register) -d '{"tenant":"t1","feature_id":"f1","schema":{},"consented":true}' -H "Content-Type:application/json" > /reports/I.1.1_register.json || true

```

### I.1.2 — Federated Trainer Orchestrator
**Branch:** `prod-feature/I.1.2-federated-trainer`  
**Files**
```

services/federated-trainer/main.py
services/federated-trainer/orchestrator.py
services/federated-trainer/tests/test_orchestrator.py
reports/I.1.2_federated_trainer.md

```
**Endpoints**
- `POST /train/round` start federated round `{model_id, tenants[], params}`
- `GET /train/status/{id}`
**Behavior**
- Validate cosign-signed manifest for production rounds (P2).
- Use secure aggregation protocol (simulate if libs missing).
**Verification**
```

pytest -q services/federated-trainer/tests/test_orchestrator.py > /reports/logs/I.1.2.log 2>&1 || true
curl -s -X POST [http://localhost:9002/train/round](http://localhost:9002/train/round) -d '{"model_id":"m1","tenants":["t1"]}' -H "Content-Type:application/json" > /reports/I.1.2_round.json || true

```

### I.1.3 — Model Exchange Bus
**Branch:** `prod-feature/I.1.3-model-exchange`  
**Files**
```

services/model-exchange-bus/main.py
services/model-exchange-bus/storage.py
services/model-exchange-bus/tests/test_exchange.py
reports/I.1.3_model_exchange.md

```
**Endpoints**
- `POST /models/upload` (multipart: signed package)
- `GET /models/{id}/download`
**Behavior**
- Verify cosign signature, record audit hash, push to model store or mirror.
**Verification**
```

pytest -q services/model-exchange-bus/tests/test_exchange.py > /reports/logs/I.1.3.log 2>&1 || true
curl -s [http://localhost:9003/health](http://localhost:9003/health) > /reports/I.1.3_health.json || true

```

### I.1.4 — Global Inference Router
**Branch:** `prod-feature/I.1.4-inference-router`  
**Files**
```

services/global-inference-router/main.py
services/global-inference-router/router.py
services/global-inference-router/tests/test_router.py
reports/I.1.4_inference_router.md

```
**Endpoints**
- `POST /invoke` {tenant, model_id, input, preferences}
**Behavior**
- Select best region/runtime based on policy, latency, cost, and fabric score.
- Route request, inject audit header, aggregate metrics.
**Verification**
```

pytest -q services/global-inference-router/tests/test_router.py > /reports/logs/I.1.4.log 2>&1 || true
curl -s -X POST [http://localhost:9004/invoke](http://localhost:9004/invoke) -d '{"tenant":"t1","model_id":"m1","input":{}}' -H "Content-Type:application/json" > /reports/I.1.4_invoke.json || true

```

### I.1.5 — Continuous Policy Feedback Loop
**Branch:** `prod-feature/I.1.5-policy-feedback`  
**Files**
```

services/policy-feedback-loop/main.py
services/policy-feedback-loop/aggregator.py
services/policy-feedback-loop/tests/test_feedback.py
reports/I.1.5_policy_feedback.md

```
**Behavior**
- Consume fabric telemetry and governance decisions.
- Generate proposed policy changes and publish signed manifests to Policy Hub (simulate).
**Verification**
```

pytest -q services/policy-feedback-loop/tests/test_feedback.py > /reports/logs/I.1.5.log 2>&1 || true
curl -s [http://localhost:9005/health](http://localhost:9005/health) > /reports/I.1.5_health.json || true

```

### I.1.6 — Fabric Scorecard & Auto-tuner
**Branch:** `prod-feature/I.1.6-fabric-scorecard`  
**Files**
```

services/fabric-scorecard/main.py
services/fabric-scorecard/tuner.py
services/fabric-scorecard/tests/test_scorecard.py
reports/I.1.6_fabric_scorecard.md

```
**Behavior**
- Aggregate model metrics, fairness checks, drift signals, resilience scores.
- Emit tuner suggestions (can be auto-apply only in non-production or with approver).
**Verification**
```

pytest -q services/fabric-scorecard/tests/test_scorecard.py > /reports/logs/I.1.6.log 2>&1 || true
curl -s [http://localhost:9006/metrics](http://localhost:9006/metrics) > /reports/I.1.6_metrics.txt || true

```

---

## Precheck (agent-run)

Create `/reports/logs/I.1_precheck.log` and `/reports/I.1_precheck.json`. Agent runs:

```

mkdir -p reports/logs
python - <<'PY' > reports/logs/I.1_precheck.log 2>&1
import os,json
r={}
envs=['GLOBAL_REGISTRY_URL','POSTGRES_DSN','VAULT_ADDR','COSIGN_KEY_PATH','NEURAL_FABRIC_URL','QUANTUM_COORD_URL']
for e in envs: r[e]= 'SET' if os.getenv(e) else 'MISSING'
r['SIMULATION_MODE']= os.getenv('SIMULATION_MODE','true')
print(json.dumps(r,indent=2))
PY
python - <<'PY' > reports/I.1_precheck.json
import json
d=json.load(open('reports/logs/I.1_precheck.log'))
print(json.dumps(d))
PY

```

Decision logic:
- If GLOBAL_REGISTRY_URL missing → `PROCEED_SIMULATION`
- If POSTGRES_DSN missing → `PROCEED_SIMULATION`
- If VAULT_ADDR or COSIGN_KEY_PATH missing → `PROCEED_SIMULATION` but mark P2 BLOCKED.

---

## Integration tests (end-to-end)

Create `tests/integration/test_I.1_end2end.py` to exercise one federated round and an inference routing. Run:

```

pytest -q tests/integration/test_I.1_end2end.py > /reports/logs/I.1_end2end.log 2>&1 || true

```

Make tests tolerant: accept simulation-mode outcomes.

---

## Verification & reporting

For each task produce `/reports/I.1.*.md` with:
- Branch name and commit SHA
- Precheck summary and `SIMULATION_MODE`
- Tests PASS/FAIL counts and excerpts
- Verification curl outputs
- Policy matrix (P1–P7) with PASS/BLOCKED flags
- Audit SHA refs (no raw data)
- Blockers and next steps

Agent must also produce `/reports/PhaseI.1_Snapshot.json` via `scripts/generate_phase_snapshot.py`.

---

## Deliverables

- All `services/*` implemented with tests and `config.example.yaml`
- `infra/diagrams/Phase_I.1_Architecture.svg`
- `/docs/policies/global_intel_policy.md`
- `/reports/I.1.*.md` + logs
- `tests/integration/test_I.1_end2end.py`
- `/reports/PhaseI.1_Snapshot.json`

---

## Agent execution rules

1. Run precheck. If decision `BLOCK` create `/reports/PhaseI.1_precheck_block.txt` and stop.
2. For each I.1.x:
   - `git checkout -b prod-feature/I.1.x-<short>`
   - Create files listed
   - Run unit tests and save logs `/reports/logs/I.1.x.log`
   - Start service locally (uvicorn) if needed for verification
   - Run verification curl commands and save outputs under `/reports/`
   - Commit locally with message `feat(I.1.x): <short> implemented (agent)`
   - Do not push or create PRs automatically.
3. After all tasks run integration tests and produce snapshot.
4. Always redact secrets. Never log secrets or raw PII.
5. If production activation desired, require human review for enabling `SIMULATION_MODE=false` and to supply VAULT/COSIGN configuration.

---

## Embedded agent prompt

```

You are the ATOM coding agent. Execute Phase I.1 per /docs/Phase_I.1_Global_Intelligence_Fabric_Agent.md. Run precheck. If critical infra missing set SIMULATION_MODE=true and annotate reports. Implement tasks I.1.1→I.1.6, create services, tests, diagrams, and reports. Commit locally per task. Do not push or create PRs. Never log secrets. Enforce P1–P7. Start now and complete autonomously.

```

---
```


