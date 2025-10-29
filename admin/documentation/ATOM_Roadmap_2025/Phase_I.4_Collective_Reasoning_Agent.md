```markdown
# Phase I.4 — Collective Reasoning & Federated Decision Fabric (Agent-Ready .md)

**Phase:** I.4 — Collective Reasoning & Federated Decision Fabric  
**Objective:** Build federated, policy-aware multi-agent decision fabric that enables coordinated, explainable decisions across regions and tenants. Provide negotiation, consensus, confidence scoring, human-in-loop approval gates, and rollback. All operations must enforce P1–P7 policies from `/docs/policies/POLICIES.md`. Agent must run autonomously. Use simulation mode when infra missing.

**Version target:** v9.3.0-phaseI.4  
**Branch prefix (local):** `prod-feature/I.4.<task>`  
**Mode:** Autonomous / Simulation fallback ready

---

## Environment variables (agent reads / honors)
```

POSTGRES_DSN
VAULT_ADDR
COSIGN_KEY_PATH
GLOBAL_REGISTRY_URL
FEDERATION_TOKEN
SIMULATION_MODE
REDIS_URL
KAFKA_URL
PROM_URL
NEURAL_FABRIC_URL
QUANTUM_PROVIDER
PHASE_I4_DECISION_TIMEOUT_MS   # default 30000

```
If any critical var missing agent must set `SIMULATION_MODE=true` and record missing items in precheck.

---

## Policies enforced (must be referenced in each task)
Refer to `/docs/policies/POLICIES.md`. Enforce additionally:

- **P1 Data Privacy:** Decision inputs that contain PII must be redacted or require tenant explicit consent. No raw PII persisted without signed manifest.
- **P2 Secrets & Signing:** All decision policies, manifests and consensus bundles must be cosign-signed prior to enactment in production.
- **P3 Execution Safety:** Any decision with impact level `high` requires manual approver recorded and dry-run pass.
- **P4 Observability:** All services expose `/health` and `/metrics`. Decision traces must be auditable.
- **P5 Multi-Tenancy:** Decisions scoped to tenant. Cross-tenant proposals require explicit policy approval.
- **P6 Performance Budget:** Consensus should complete within `PHASE_I4_DECISION_TIMEOUT_MS` where possible. Long-running negotiations must be async with progress telemetry.
- **P7 Resilience & Recovery:** All decision outcomes must be reversible where feasible. Pre/post state snapshots recorded with SHA256.

---

## High-level tasks (I.4.1 → I.4.7)
| ID | Task | Goal |
|----|------|------|
| I.4.1 | Decision Coordinator | Orchestrate proposals, votes, consensus, and enactment |
| I.4.2 | Proposal Composer | Create signed decision manifests from inputs and models |
| I.4.3 | Federated Negotiator | Multi-region agent negotiation engine with consensus algorithms (raft-style or quorum) |
| I.4.4 | Confidence Scorer | Produce confidence, risk, cost tradeoff metrics and explanation text |
| I.4.5 | Human-in-Loop Gateway | Approval UI endpoints, multi-channel notifications, MFA hooks |
| I.4.6 | Decision Auditor | Immutable trace store with PQC signatures and rollback helpers |
| I.4.7 | Simulation & Canary Runner | Replay decisions, dry-run validations, canary rollouts and rollback tests |

---

## Files & directories to create (exact list)
```

services/decision-coordinator/
services/proposal-composer/
services/federated-negotiator/
services/confidence-scorer/
services/hil-gateway/
services/decision-auditor/
services/sim-canary/
infra/helm/decision-fabric/
infra/sql/i4_decision_schema.sql
docs/policies/decision_policy.md
tests/integration/test_I.4_end2end.py
reports/
scripts/generate_phase_snapshot.py   # reuse if exists

```
Each `services/*` must include: `main.py`, `requirements.txt`, `Dockerfile`, `config.example.yaml`, `tests/`, and Prometheus metrics hooks.

---

## Task details

### I.4.1 — Decision Coordinator
**Branch (local):** `prod-feature/I.4.1-decision-coordinator`  
**Files**
```

services/decision-coordinator/main.py
services/decision-coordinator/coordinator.py
services/decision-coordinator/models.py
services/decision-coordinator/tests/test_coordinator.py
reports/I.4.1_decision_coordinator.md

```
**Endpoints**
- `POST /proposals` → submit `{tenant_id, manifest, metadata}`. Requires JWT tenant claim (P5).
- `GET /proposals/{id}` → status + vote results.
- `POST /proposals/{id}/enact` → enact outcome (requires approver if impact high).
- `GET /health` `GET /metrics`
**Behavior**
- Validate manifest signature (cosign) in production.
- Broadcast proposal to negotiator and confidence scorer.
- Persist proposal and pre-state snapshot SHA256 to DB.
**Verification**
```

pytest -q services/decision-coordinator/tests/test_coordinator.py > /reports/logs/I.4.1.log 2>&1 || true
curl -s -X POST [http://localhost:9201/proposals](http://localhost:9201/proposals) -H "Content-Type:application/json" -d '{"tenant_id":"t1","manifest":{"action":"scale","target":"serviceX"}}' > /reports/I.4.1_post.json || true

```

---

### I.4.2 — Proposal Composer
**Branch:** `prod-feature/I.4.2-proposal-composer`  
**Files**
```

services/proposal-composer/main.py
services/proposal-composer/composer.py
services/proposal-composer/templates.yaml
services/proposal-composer/tests/test_composer.py
reports/I.4.2_proposal_composer.md

```
**Endpoints**
- `POST /compose` → input signals, returns signed manifest (cosign simulated).
- `GET /templates` → list composer templates
**Behavior**
- Use neural fabric / model suggestions to populate manifests.
- Redact PII unless tenant consent provided.
**Verification**
```

pytest -q services/proposal-composer/tests/test_composer.py > /reports/logs/I.4.2.log 2>&1 || true
curl -s -X POST [http://localhost:9202/compose](http://localhost:9202/compose) -d '{"context":"reduce cost","tenant_id":"t1"}' > /reports/I.4.2_compose.json || true

```

---

### I.4.3 — Federated Negotiator
**Branch:** `prod-feature/I.4.3-federated-negotiator`  
**Files**
```

services/federated-negotiator/main.py
services/federated-negotiator/negotiator.py
services/federated-negotiator/consensus.py
services/federated-negotiator/tests/test_negotiator.py
reports/I.4.3_federated_negotiator.md

```
**Endpoints**
- `POST /negotiate` → accepts proposal id, starts negotiation across regions
- `GET /negotiate/{id}/status` → negotiation progress
**Behavior**
- Implement quorum-based voting simulation if cross-region not available.
- Enforce timeouts and progress telemetry.
**Verification**
```

pytest -q services/federated-negotiator/tests/test_negotiator.py > /reports/logs/I.4.3.log 2>&1 || true
curl -s -X POST [http://localhost:9203/negotiate](http://localhost:9203/negotiate) -d '{"proposal_id":"p1"}' > /reports/I.4.3_negotiate.json || true

```

---

### I.4.4 — Confidence Scorer
**Branch:** `prod-feature/I.4.4-confidence-scorer`  
**Files**
```

services/confidence-scorer/main.py
services/confidence-scorer/scorer.py
services/confidence-scorer/tests/test_scorer.py
reports/I.4.4_confidence_scorer.md

```
**Endpoints**
- `POST /score` → returns `{confidence, risk, cost_estimate, explanation}`
**Behavior**
- Use models from Neural Fabric + historical metrics to compute score.
- Provide human-readable explanation strings.
**Verification**
```

pytest -q services/confidence-scorer/tests/test_scorer.py > /reports/logs/I.4.4.log 2>&1 || true
curl -s -X POST [http://localhost:9204/score](http://localhost:9204/score) -d '{"proposal_id":"p1"}' > /reports/I.4.4_score.json || true

```

---

### I.4.5 — Human-in-Loop Gateway (HIL)
**Branch:** `prod-feature/I.4.5-hil-gateway`  
**Files**
```

services/hil-gateway/main.py
services/hil-gateway/notify.py
services/hil-gateway/tests/test_hil.py
reports/I.4.5_hil_gateway.md

```
**Endpoints**
- `POST /approve/{proposal_id}` → approve/reject with approver id & proof
- `GET /pending/{tenant_id}` → list pending approvals
**Behavior**
- Send notifications via email/telegram/slack (simulate). Record approver, MFA status.
- For production require approver signature and cosign on final manifest for enactment (P2/P3).
**Verification**
```

pytest -q services/hil-gateway/tests/test_hil.py > /reports/logs/I.4.5.log 2>&1 || true
curl -s [http://localhost:9205/pending/t1](http://localhost:9205/pending/t1) > /reports/I.4.5_pending.json || true

```

---

### I.4.6 — Decision Auditor
**Branch:** `prod-feature/I.4.6-decision-auditor`  
**Files**
```

services/decision-auditor/main.py
services/decision-auditor/audit_store.py
services/decision-auditor/tests/test_audit.py
reports/I.4.6_decision_auditor.md

```
**Endpoints**
- `GET /audit/{proposal_id}` → full audit trace (no raw secrets or PII)
- `POST /snapshot/{proposal_id}` → store pre/post snapshot hash references
**Behavior**
- Store immutable audit entries with SHA256 and PQC signature simulation.
- Provide rollback helper endpoints (dry-run only in simulation).
**Verification**
```

pytest -q services/decision-auditor/tests/test_audit.py > /reports/logs/I.4.6.log 2>&1 || true
curl -s [http://localhost:9206/audit/p1](http://localhost:9206/audit/p1) > /reports/I.4.6_audit.json || true

```

---

### I.4.7 — Simulation & Canary Runner
**Branch:** `prod-feature/I.4.7-sim-canary`  
**Files**
```

services/sim-canary/main.py
services/sim-canary/canary.py
services/sim-canary/tests/test_canary.py
reports/I.4.7_sim_canary.md

```
**Endpoints**
- `POST /canary/run` → run canary/dry-run for proposal id
- `GET /canary/{id}/result`
**Behavior**
- Execute a full dry-run: composer → negotiator (simulation) → scorer → HIL dry-run → auditor snapshots.
- Produce scorecard and canary metrics.
**Verification**
```

pytest -q services/sim-canary/tests/test_canary.py > /reports/logs/I.4.7.log 2>&1 || true
curl -s -X POST [http://localhost:9207/canary/run](http://localhost:9207/canary/run) -d '{"proposal_id":"p1","dry_run":true}' > /reports/I.4.7_canary.json || true

```

---

## Integration test (end-to-end)
Create `tests/integration/test_I.4_end2end.py` to:
* Compose proposal via composer
* Submit proposal to coordinator
* Run negotiation
* Score confidence
* Trigger HIL dry-run and approval (simulate)
* Enact or rollback and audit trace

Run:
```

pytest -q tests/integration/test_I.4_end2end.py > /reports/logs/I.4_end2end.log 2>&1 || true

```

---

## Compliance precheck (agent must run before implementation)
Create `/docs/compliance-precheck_I.4.md` with minimal checks:
- Verify `GLOBAL_REGISTRY_URL` reachable
- Vault & Cosign presence
- Postgres reachability
- Neural Fabric / Quantum provider reachable (or mark simulation)
Agent must write `/reports/I.4_precheck.json` and `/reports/logs/I.4_precheck.log`.

Example decision logic:
- All services reachable → `PROCEED`
- Partial missing → `PROCEED_SIMULATION`
- Registry missing → `BLOCK` (stop)

---

## Verification commands summary (agent must save outputs under `/reports/`)
```

# unit tests per service (already listed above)

pytest -q tests/integration/test_I.4_end2end.py > /reports/logs/I.4_end2end.log 2>&1 || true

# quick health checks

curl -s [http://localhost:9201/health](http://localhost:9201/health) > /reports/I.4.1_health.json || true
curl -s [http://localhost:9203/negotiate](http://localhost:9203/negotiate) -d '{"proposal_id":"p1"}' > /reports/I.4.3_negotiate.json || true
curl -s -X POST [http://localhost:9207/canary/run](http://localhost:9207/canary/run) -d '{"proposal_id":"p1","dry_run":true}' > /reports/I.4.7_canary.json || true

```

---

## Reporting (per-task + phase)
For each task create `/reports/I.4.<task>_<short>.md` containing:
- Branch and commit SHA
- Precheck summary and `SIMULATION_MODE` flag
- Tests run and PASS/FAIL counts with log snippets
- Verification outputs (health, negotiate, canary)
- Policy matrix P1–P7 with PASS/BLOCKED notes
- Audit SHA256 references (no raw data)
- Blockers and remediation steps

Also produce `/reports/PhaseI.4_Snapshot.json` via `scripts/generate_phase_snapshot.py`.

---

## Failure handling & simulation rules (mandatory)
- If external infra missing, use `/providers/mock_*` implementations under each service.
- Never write secrets or tokens to logs. Replace with `<REDACTED>`.
- If a proposal contains PII without consent, coordinator must reject with `403` unless manifest includes signed consent.
- High-impact decisions must default to `dry_run: true` until explicit approver recorded.
- All enacted changes must include pre/post state snapshots and corresponding SHA256 hashes recorded in `decision_auditor`.

---

## Deliverables (agent must produce)
* `services/*` per task with tests and config
* `tests/integration/test_I.4_end2end.py`
* `/docs/compliance-precheck_I.4.md`
* `/docs/policies/decision_policy.md`
* `/reports/I.4.*.md` and `/reports/logs/I.4.*.log`
* `/reports/PhaseI.4_Snapshot.json`
* Local git commits on branches `prod-feature/I.4.x-<short>` with clear messages (do not auto-push unless infra requires)

---

## Embedded Agent Prompt (copy exactly and use)
You are the ATOM coding agent.
Execute Phase I.4 — Collective Reasoning & Federated Decision Fabric per this document.
1. Run `docs/compliance-precheck_I.4.md`. If decision == BLOCK stop and write `/reports/PhaseI.4_block.txt`.
2. For each I.4.x task in order:
   - `git checkout -b prod-feature/I.4.x-<short>`
   - Create files and stubs as specified.
   - Run unit tests, save logs to `/reports/logs/`.
   - Run verification commands and save outputs to `/reports/`.
   - Produce `/reports/I.4.x_<short>.md` with policy matrix and artifacts.
   - Commit locally: `git add . && git commit -m "feat(I.4.x): <short> implemented (agent)"`
   - Do not auto-create PRs or push branches unless instructed by a human reviewer.
3. After all tasks:
   - Run integration tests and save `/reports/logs/I.4_end2end.log`.
   - Run `python scripts/generate_phase_snapshot.py` to create `/reports/PhaseI.4_Snapshot.json`.
   - Create `/reports/PhaseI.4_final_summary.md` consolidating all task reports and listing blockers and manual next steps.
4. Safety rules:
   - Do not log secrets.
   - Enforce P1–P7 for every action.
   - High-impact proposals require approver and cosign-signed manifests.
5. If simulation required set `SIMULATION_MODE=true` and proceed. Mark all blocked infra in reports.

Execute autonomously and produce the files and reports described. End.

---

## Notes for human operator
- Review `/reports/I.4_precheck.json` before any manual push to production branches.
- For production activation ensure Vault, Cosign, Neural Fabric, and cross-region registry are configured and reachable.
- Manual review required for any high-impact decision enactment and tag recommendation `v9.3.0-phaseI.4`.

---  
End of `Phase_I.4_Collective_Reasoning_Agent.md`
```
