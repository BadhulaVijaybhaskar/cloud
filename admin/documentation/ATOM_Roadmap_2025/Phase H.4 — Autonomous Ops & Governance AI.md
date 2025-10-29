Proceeding. Below is the **agent-ready `.md`** for **Phase H.4 — Autonomous Ops & Governance AI**. Drop this file at `/docs/Phase_H.4_Autonomous_Ops_Governance.md`. The agent can run it end-to-end without extra prompts. It includes prechecks, env vars, task list, files to create, endpoints, policy hooks (P1–P7), verification commands, testing, reporting, and failure handling.

```markdown
# Phase H.4 — Autonomous Ops & Governance AI (Agent-Ready .md)

**Phase:** H.4 — Autonomous Ops & Governance AI  
**Goal:** Implement the governance AI that autonomously observes, reasons, and acts to maintain policy compliance, cost/perf budgets, and security across ATOM Cloud. Provide safe human-in-the-loop controls for high-risk actions. Deliver microservices, models, policy agents, audit trails, and verification logic. Simulation-friendly.  
**Version target:** v8.3.0-phaseH.4  
**Branch prefix (local):** prod-feature/H.4.<task>  
**Mode:** Autonomous / SIMULATION fallback ready

---

## 1 — Summary & Intent
Build an Autonomous Governance layer that continuously monitors metrics and logs, scores risk, proposes and optionally applies remediations (scaling, failover, policy rollbacks, key rotation), and performs cost optimization. All actions must respect P1–P7 and require approvals for production-critical changes. Provide telemetry, policy explainability, and auditability.

---

## 2 — Required environment variables
```

POSTGRES_DSN
VAULT_ADDR
COSIGN_KEY_PATH
PROM_URL
KAFKA_URL
REDIS_URL
SIMULATION_MODE
OPENAI_KEY
NEURAL_FABRIC_MODE
GLOBAL_REGISTRY_URL
ADMIN_APPROVER_EMAIL
SLACK_WEBHOOK_URL
TELEGRAM_BOT_TOKEN

```
If any *critical* var missing agent sets `SIMULATION_MODE=true` and records missing items.

---

## 3 — Policies enforced (P1–P7)
- **P1 Data Privacy:** No PII in model input. All user inputs hashed/redacted. Consent checks for PII-affecting actions.  
- **P2 Secrets & Signing:** Any action that changes keys, deploys signed artifacts, or alters policy must be cosign-signed and logged.  
- **P3 Execution Safety:** High-risk actions require approver; default dry-run for production. Autonomy limited by risk tiers.  
- **P4 Observability:** All services expose `/health` and `/metrics`. Governance decisions produce explainable logs.  
- **P5 Multi-Tenancy:** Tenant-scoped actions only. Global actions required separate approval.  
- **P6 Performance Budget:** Remediation actions must meet p95 execution time budgets.  
- **P7 Resilience & Recovery:** All actions are reversible; snapshot + rollback created before changes.

---

## 4 — High-level tasks (H.4.1 → H.4.8)
| ID | Task | Goal |
|----|------|------|
| H.4.1 | Observability Ingestor | Centralize metrics/logs/traces; normalize into vector store |
| H.4.2 | Risk Scoring Engine | Continuous risk scoring per tenant/service (security, cost, performance) |
| H.4.3 | Policy Reasoner (AI) | LLM+Neural agent that maps risk -> candidate remediations with explanation |
| H.4.4 | Action Orchestrator | Execute safe remediations (scale, restart, rollback, rotate keys) with dry-run & approvals |
| H.4.5 | Explainability & Audit | Produce human-readable justification and cryptographic audit trail (PQC ready) |
| H.4.6 | Approval Gateway | Human-in-the-loop approval flows via Slack/Telegram/Email with TTL and MFA option |
| H.4.7 | Cost Optimizer | Predictive cost model + proposed infra changes for cost/perf tradeoffs |
| H.4.8 | Simulation & Canary Runner | Safe simulation sandbox & canary deployments for proposed actions |

---

## 5 — Files & directories (exact list agent must create)
```

services/observability-ingestor/
services/risk-scoring/
services/policy-reasoner/
services/action-orchestrator/
services/explain-audit/
services/approval-gateway/
services/cost-optimizer/
services/simulation-runner/
infra/helm/h4-governance/
docs/policies/governance_policy.md
tests/integration/test_H.4_end2end.py
reports/
scripts/generate_phase_snapshot.py

```
Each service must include: `main.py`, `requirements.txt`, `Dockerfile`, `config.example.yaml`, `tests/`, and expose `/health` and `/metrics`.

---

## 6 — Task details

### H.4.1 Observability Ingestor
**Branch:** prod-feature/H.4.1-observability-ingestor  
**Files**
```

services/observability-ingestor/main.py
services/observability-ingestor/parser.py
services/observability-ingestor/vectorizer.py
services/observability-ingestor/tests/test_ingest.py
reports/H.4.1_observability.md

```
**Behavior**
- Pull from Prometheus, Loki, Kafka, and system logs.
- Normalize events to JSONL.
- Extract features and embed into vector DB (local SQLite + FAISS mock if remote unavailable).
- Tag by tenant, service, and severity.
**Endpoints**
- POST `/ingest/event` (for manual events)
- GET `/health` `/metrics`
**Verification**
```

pytest -q services/observability-ingestor/tests/test_ingest.py > /reports/logs/H.4.1.log 2>&1 || true
curl -s [http://localhost:8801/health](http://localhost:8801/health) > /reports/H.4.1_health.json || true

```

### H.4.2 Risk Scoring Engine
**Branch:** prod-feature/H.4.2-risk-scoring  
**Files**
```

services/risk-scoring/main.py
services/risk-scoring/scorer.py
services/risk-scoring/tests/test_scoring.py
reports/H.4.2_risk_scoring.md

```
**Behavior**
- Continuous scoring using rules + ML model (simulated).
- Output risk vectors and severity levels (low/med/high/critical).
- Persist scores to Postgres table `governance_risks`.
**Endpoints**
- GET `/risk/{tenant_id}` -> latest score
**Verification**
```

pytest -q services/risk-scoring/tests/test_scoring.py > /reports/logs/H.4.2.log 2>&1 || true
curl -s [http://localhost:8802/risk/test_tenant](http://localhost:8802/risk/test_tenant) > /reports/H.4.2_risk.json || true

```

### H.4.3 Policy Reasoner (AI)
**Branch:** prod-feature/H.4.3-policy-reasoner  
**Files**
```

services/policy-reasoner/main.py
services/policy-reasoner/reasoner.py
services/policy-reasoner/models/intent_prompt.md
services/policy-reasoner/tests/test_reasoner.py
reports/H.4.3_policy_reasoner.md

```
**Behavior**
- Use LLM (OpenAI or local simulation) with RAG from observability vectors to propose ranked remediations.
- Return action plan with rationale, risk delta, and required approvals.
- Redact PII from inputs.
**Endpoints**
- POST `/propose` {tenant_id, context_id, risk_id} -> proposals
**Verification**
```

pytest -q services/policy-reasoner/tests/test_reasoner.py > /reports/logs/H.4.3.log 2>&1 || true
curl -s -X POST [http://localhost:8803/propose](http://localhost:8803/propose) -d '{"tenant_id":"test","context_id":"c1","risk_id":"r1"}' -H 'Content-Type:application/json' > /reports/H.4.3_proposals.json || true

```

### H.4.4 Action Orchestrator
**Branch:** prod-feature/H.4.4-action-orchestrator  
**Files**
```

services/action-orchestrator/main.py
services/action-orchestrator/orchestrator.py
services/action-orchestrator/drivers/ (k8s/aws/gcloud/mock)
services/action-orchestrator/tests/test_orchestrator.py
reports/H.4.4_action_orchestrator.md

```
**Behavior**
- Execute authorized actions: scale, restart, rollback, rotate-keys, failover.
- Always create snapshot + cosign-signed manifest before action.
- Dry-run default in production unless approved.
**Endpoints**
- POST `/execute` {action_plan, approver_token?}
- GET `/status/{exec_id}`
**Verification**
```

pytest -q services/action-orchestrator/tests/test_orchestrator.py > /reports/logs/H.4.4.log 2>&1 || true
curl -s -X POST [http://localhost:8804/execute](http://localhost:8804/execute) -d '{"action":"scale","tenant_id":"t1","target":"service-x","replicas":3}' -H 'Content-Type:application/json' > /reports/H.4.4_exec.json || true

```

### H.4.5 Explainability & Audit
**Branch:** prod-feature/H.4.5-explain-audit  
**Files**
```

services/explain-audit/main.py
services/explain-audit/audit_helper.py
services/explain-audit/tests/test_audit.py
reports/H.4.5_explain_audit.md

```
**Behavior**
- Produce human-readable justification for each proposal and final action.
- Store immutable audit entries with SHA256 + PQC signature placeholder.
- Provide `/audit/{id}` endpoint returning explainable log (no secrets).
**Verification**
```

pytest -q services/explain-audit/tests/test_audit.py > /reports/logs/H.4.5.log 2>&1 || true
curl -s [http://localhost:8805/audit/test-id](http://localhost:8805/audit/test-id) > /reports/H.4.5_audit.json || true

```

### H.4.6 Approval Gateway
**Branch:** prod-feature/H.4.6-approval-gateway  
**Files**
```

services/approval-gateway/main.py
services/approval-gateway/notify.py
services/approval-gateway/tests/test_notify.py
reports/H.4.6_approval_gateway.md

```
**Behavior**
- Send approval requests via Slack/Telegram/Email webhook.
- Receive approvals with signed token and optional MFA step.
- Approval TTL and auto-expire rules.
**Endpoints**
- POST `/request_approval` -> sends notification
- POST `/approve` -> receives approval token
**Verification**
```

pytest -q services/approval-gateway/tests/test_notify.py > /reports/logs/H.4.6.log 2>&1 || true
curl -s -X POST [http://localhost:8806/request_approval](http://localhost:8806/request_approval) -d '{"exec_id":"e1","approver":"admin"}' -H 'Content-Type:application/json' > /reports/H.4.6_req.json || true

```

### H.4.7 Cost Optimizer
**Branch:** prod-feature/H.4.7-cost-optimizer  
**Files**
```

services/cost-optimizer/main.py
services/cost-optimizer/model.py
services/cost-optimizer/tests/test_cost.py
reports/H.4.7_cost_optimizer.md

```
**Behavior**
- Predict future infra cost per tenant and recommend rightsizing.
- Simulate cost delta for action plans.
**Endpoints**
- GET `/cost/forecast/{tenant_id}`
**Verification**
```

pytest -q services/cost-optimizer/tests/test_cost.py > /reports/logs/H.4.7.log 2>&1 || true
curl -s [http://localhost:8807/cost/forecast/test_tenant](http://localhost:8807/cost/forecast/test_tenant) > /reports/H.4.7_cost.json || true

```

### H.4.8 Simulation & Canary Runner
**Branch:** prod-feature/H.4.8-simulation-runner  
**Files**
```

services/simulation-runner/main.py
services/simulation-runner/tests/test_sim.py
reports/H.4.8_simulation.md

```
**Behavior**
- Create canary environments, run action plans in sandbox, evaluate impact, produce scorecard.
- Replay historical events for model validation.
**Verification**
```

pytest -q services/simulation-runner/tests/test_sim.py > /reports/logs/H.4.8.log 2>&1 || true
python services/simulation-runner/main.py --run-sim > /reports/H.4.8_sim.txt 2>&1 || true

```

---

## 7 — Integration test (end-to-end)
Create `tests/integration/test_H.4_end2end.py` which:
- Simulates ingest events -> risk score -> policy reasoner proposals -> sends approval request -> executes in dry-run -> runs simulation canary -> writes audit.
Run:
```

pytest -q tests/integration/test_H.4_end2end.py > /reports/logs/H.4_end2end.log 2>&1 || true

```

---

## 8 — Precheck & decision logic
Agent must run precheck and create `/reports/H.4_precheck.json`. If `SIMULATION_MODE` already true proceed in simulation. If `VAULT_ADDR` or `POSTGRES_DSN` missing mark blockers. Example checks:
- Vault reachable
- Postgres reachable
- Prometheus reachable
- OpenAI/LLM key presence
- Slack/Telegram webhook presence for approvals

If any critical item missing, set `SIMULATION_MODE=true` and continue. Write decisions in `/reports/H.4_precheck.json`.

---

## 9 — Reporting requirements (one per task)
Each `/reports/H.4.<task>_<short>.md` must include:
- Branch and commit SHA
- SIMULATION_MODE status and missing infra
- Tests run and PASS/FAIL counts
- Verification outputs (snippets)
- Policy table P1–P7 PASS/BLOCKED/FAIL
- Audit log SHA256 refs (no raw secrets)
- Blockers and remediation steps

Aggregate final `/reports/PhaseH.4_Snapshot.json`.

---

## 10 — Execution steps (agent sequence)
1. Run precheck. If `BLOCK` write `/reports/H.4_precheck_block.txt` and stop. If `PROCEED_SIMULATION` continue in simulation.
2. For each task H.4.1 → H.4.8:
   - `git checkout -b prod-feature/H.4.x-<short>`
   - Generate service files per spec
   - Run unit tests
   - Run verification curl commands
   - Write `/reports/H.4.x_<short>.md`
   - Commit locally: `git add . && git commit -m "feat(H.4.x): <short> (agent)"`
   - Do NOT push or create PR automatically (leave for human review)
3. Run integration tests and save logs.
4. Generate snapshot: `python scripts/generate_phase_snapshot.py`
5. Create final `/reports/PhaseH.4_final_summary.md` consolidating task reports and recommended tag `v8.3.0-phaseH.4`.

---

## 11 — Failure handling & safety
- Never log secrets or tokens. Replace with `<REDACTED>`.
- High-risk actions must default to dry-run and require approver when `ENV=production`.
- If policy reasoner suggests sensitive changes (key rotation, cross-tenant change), require cosign-signed manifest plus human approver.
- For any action executed, capture pre-state snapshot and include SHA256 in audit.

---

## 12 — Deliverables
- 8 microservices with tests and metrics
- Integration test suite
- Precheck and simulation tooling
- Governance policy docs: `docs/policies/governance_policy.md`
- Reports and snapshot: `/reports/PhaseH.4_Snapshot.json`, `/reports/PhaseH.4_final_summary.md`
- Tag recommendation: `v8.3.0-phaseH.4`

---

## 13 — Embedded agent prompt (copy into agent runtime)
```

You are the ATOM coding agent. Execute Phase H.4 per /docs/Phase_H.4_Autonomous_Ops_Governance.md. Run precheck. If infra missing set SIMULATION_MODE=true and proceed. Implement H.4.1→H.4.8, run tests, generate reports, commit locally, and produce final snapshot. Do not push branches or open PRs. Do not log secrets. Require approver for production-critical actions. Preserve auditability and policy compliance. Stop and write /reports/H.4_precheck_block.txt if precheck returns BLOCK.

```

---

## 14 — Quick verification commands summary
```

curl -s [http://localhost:8801/health](http://localhost:8801/health) > /reports/H.4.1_health.json || true
curl -s [http://localhost:8802/risk/test_tenant](http://localhost:8802/risk/test_tenant) > /reports/H.4.2_risk.json || true
curl -s -X POST [http://localhost:8803/propose](http://localhost:8803/propose) -d '{"tenant_id":"test","context_id":"c1","risk_id":"r1"}' -H 'Content-Type:application/json' > /reports/H.4.3_proposals.json || true
curl -s -X POST [http://localhost:8804/execute](http://localhost:8804/execute) -d '{"action":"dryrun","tenant_id":"t1"}' -H 'Content-Type:application/json' > /reports/H.4.4_exec.json || true
curl -s [http://localhost:8805/audit/test-id](http://localhost:8805/audit/test-id) > /reports/H.4.5_audit.json || true
pytest -q tests/integration/test_H.4_end2end.py > /reports/logs/H.4_end2end.log 2>&1 || true
python scripts/generate_phase_snapshot.py

```

---

## 15 — Acceptance criteria
- All services respond on `/health` and `/metrics`.
- Integration tests executed; logs saved under `/reports/logs/`.
- Each task report exists and contains policy pass/fail matrix.
- Final snapshot `/reports/PhaseH.4_Snapshot.json` created.
- High-risk actions remain dry-run unless manual approver provided.

---

## 16 — Next steps after completion
- Human review of reports and logs.
- Manual push, PRs, and deployment to staging.
- Run full end-to-end tests against real infra.
- Gradual production activation with staged approvers.

---

**End of Phase H.4 Agent-Ready Build Plan**
```


