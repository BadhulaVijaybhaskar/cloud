# `/docs/Phase_B_NeuralOps_Agent.md` — Agent-ready, drop-in, complete

Place this file at `/docs/Phase_B_NeuralOps_Agent.md` in the repo. It contains everything the coding agent needs to run Phase B (NeuralOps) end-to-end: file layout, exact tasks, commands, tests, policies, CI hooks, and the single-copy prompt to start work. The agent should create any missing helper files listed here before running tasks.

---

## One-line objective

Build **NeuralOps**: the AIOps intelligence layer on ATOM that ingests telemetry and run-history, emits signals, recommends WPKs, and safely executes remediation via the WPK registry and runtime.

**Branch prefix:** `prod-feature/B.`
**Reports dir:** `/reports/`
**Logs dir:** `/reports/logs/`
**Timeout:** Phase B MVP targeted 8–12 weeks; agent works task-by-task and opens PR per milestone.

---

## Required environment (agent must record `/reports/phaseB_prereqs.json`)

* `POSTGRES_DSN` (workflow_runs DB)
* `PROM_URL` (Prometheus)
* `VAULT_ADDR`, `VAULT_ROLE` (Vault for keys)
* `MILVUS_ENDPOINT` or `VECTOR_DB_URL` (optional)
* `OPENAI_KEY` or other embedding provider keys (optional)
* `GITHUB_TOKEN` (for PRs)
* `S3_BUCKET` + creds (for ETL exports)

Agent must write `/reports/phaseB_prereqs.json` listing present/missing items. Missing critical items mark dependent tasks BLOCKED.

---

## High-level milestones (deliverable per milestone + branch)

* **B.1 Insight Engine** — `prod-feature/B.1-insight` — `/services/insight-engine/`
  Endpoints: `POST /analyze`, `GET /signals`. Implements Z-score + EWMA detectors, correlation hints, health checks. Emits Prom metrics.
* **B.2 ETL & Vectorization** — `prod-feature/B.2-etl` — `/services/etl/`
  Exports `workflow_runs` → JSONL → embeddings → write to Milvus (or local vector store). CLI job `etl/run_vectorize.sh`.
* **B.3 Recommendation API** — `prod-feature/B.3-recommend` — `/services/recommender/`
  Endpoint: `POST /recommend` → returns top-N WPK ids, confidence score, explanation.
* **B.4 Incident Orchestrator** — `prod-feature/B.4-orchestrator` — `/services/orchestrator/`
  Implements suggest→dry-run→approval→execute flow. Audit logs. Connects to registry & runtime-agent.
* **B.5 BYOC Connector** — `prod-feature/B.5-connector` — `/services/connector/`
  Lightweight agent (k8s Daemon/Deployment) to onboard external clusters, stream metrics, accept signed triggers.
* **B.6 UI & Productization** — `prod-feature/B.6-ui` — `/ui/neuralops/`
  Minimal Next.js dashboard: incidents, recommendations, approve/run UX.

Each milestone: implement, test, docs, Helm (or docker-compose) manifest, PR.

---

## File layout to create / verify (agent must ensure these exist or create stubs)

```
services/insight-engine/
  ├─ main.py
  ├─ requirements.txt
  ├─ api/
  │   ├─ analyze.py
  │   └─ signals.py
  └─ tests/test_insight.py

services/etl/
  ├─ export_runs/
  │   └─ export_to_jsonl.py
  ├─ vectorize/
  │   └─ vectorize.py
  └─ scripts/run_vectorize.sh

services/recommender/
  ├─ main.py
  ├─ models/
  │   └─ README.md
  └─ tests/test_recommender.py

services/orchestrator/
  ├─ main.py
  ├─ engine.py
  └─ tests/test_orchestrator.py

services/connector/
  ├─ agent.py
  └─ k8s/
      └─ deployment.yaml

ui/neuralops/
  ├─ package.json
  └─ pages/
      └─ index.js

infra/helm/insight-engine/
infra/helm/recommender/
infra/helm/orchestrator/
infra/helm/connector/

docs/Phase_B_Readme.md
reports/B.*.md
reports/logs/B.*.log
```

Agent should create minimal content if missing and implement logic defined below.

---

## Detailed tasks and commands

### B.1 — Insight Engine (2–3 days)

**Goal:** Detect anomalies and produce signals.

Files to implement: `services/insight-engine/main.py`, `api/analyze.py`, `api/signals.py`.

Key behavior:

* Accept POST `/analyze` with `{prom_query, lookback, labels}` and return anomaly score, z-score, ewma, and hint.
* Periodic worker reads Prometheus queries from rules and emits signals to DB table `insight_signals`.
* Expose `/metrics` with `neuralops_signals_total`, `neuralops_anomaly_total`.

Commands:

```bash
# run locally
python -m services.insight_engine.main
pytest services/insight-engine/tests -q
curl -X POST http://localhost:8002/analyze -d '{"query":"increase(...)", "lookback":"5m"}'
```

Acceptance:

* Unit tests pass.
* `POST /analyze` returns `{"score": float, "method":"zscore|ewma", "hint":"string"}`.

### B.2 — ETL & Vectorization (2–3 days)

**Goal:** Export run-history and vectorize.

Steps:

1. Export `workflow_runs` rows to JSONL.
2. For each record produce embedding via OpenAI/HF or fallback local embedder.
3. Insert vectors into Milvus/Pinecone or local vector file.

Commands:

```bash
python services/etl/export_runs/export_to_jsonl.py --out /tmp/runs.jsonl
python services/etl/vectorize/vectorize.py --in /tmp/runs.jsonl --out /tmp/vectors.json
```

Acceptance:

* `/tmp/runs.jsonl` exists and not empty.
* `vectorize.py` writes vectors and prints summary like `N vectors written`.

### B.3 — Recommendation API (1–2 days)

**Goal:** Given incident (signal id or payload) return top-N WPKs + explanation.

Design:

* Query vector DB for similar past runs + WPK outcomes.
* Score candidate WPKs by similarity + success_rate.
* Return JSON: `[{playbook_id, score, justification}]`.

Commands:

```bash
python services/recommender/main.py  # starts at :8003
curl -X POST http://localhost:8003/recommend -d '{"signal_id":"..."}'
```

Acceptance:

* Response contains top-1 recommendation with `score` >= 0.1 (heuristic).

### B.4 — Incident Orchestrator (2–3 days)

**Goal:** Execute recommended WPKs safely.

Flow:

1. `suggest` — create incident with recommendations.
2. `dry-run` — call registry `POST /workflows/{id}/dry-run` and record decision.
3. `approve` — requires org-admin role (JWT).
4. `execute` — call runtime-agent execute endpoint and record run in `workflow_runs`.

Commands:

```bash
python services/orchestrator/main.py
curl -X POST http://localhost:8004/orchestrate -d '{"signal_id":"...","playbook_id":"..."}'
```

Acceptance:

* Orchestrator logs audit entry for each step.
* Dry-run rejects unsafe runs.

### B.5 — BYOC Connector (2–3 days)

**Goal:** Onboard external k8s cluster and stream metrics.

Behavior:

* Installable agent (k8s manifest) or binary that:

  * Scrapes local Prometheus metrics and forwards to NeuralOps via secure channel (Vault token).
  * Accepts signed WPK triggers (verifies cosign signature).
* Minimal CLI to onboard: `connector agent install --kubeconfig=... --vault-token=...`.

Commands:

```bash
python services/connector/agent.py --register --kubeconfig ~/.kube/config
```

Acceptance:

* Agent registers and heartbeat visible in `/services/connector/` status endpoint.

### B.6 — UI & Productization (2–3 days)

**Goal:** Provide dashboard for incidents, recommendations, approvals.

Minimum:

* Next.js app showing list of signals, top recommendation, approve/run buttons (calls orchestrator).
* Authentication stub (JWT) with `org-admin` role check.

Commands:

```bash
cd ui/neuralops
npm install
npm run dev
```

Acceptance:

* Web UI loads and can call `recommend` and `orchestrate` endpoints (mocked if backend missing).

---

## Policy & Safety rules (must be enforced by agent)

Agent must implement and document policy hooks:

1. **safety.mode default** = `manual`. Only playbooks with `safety.mode=auto` and `allowed_roles` including `org-admin` can be auto-executed. Document in `/docs/policies/safety.md`.
2. **cosign enforcement**: All WPKs executed must be cosign-verified. Use Vault broker for cosign keys. Stub file `services/workflow-registry/cosign_enforcer.py` must be used.
3. **audit trail**: Every recommend/dry-run/approve/execute must write an immutable audit entry to `audit_logs` plus upload SHA-256 to S3 via `infra/audit/s3_audit_logger.py`.
4. **approval policy**: Orchestrator must require explicit approver id for `execute` and record timestamp, approver, and pre/post state.
5. **data privacy**: Before vectorization, redact PII fields from `workflow_runs` per `docs/policies/data_redaction.md`. Provide redaction function.

Agent must create or update:

```
docs/policies/safety.md
docs/policies/data_redaction.md
docs/policies/approval_workflow.md
```

---

## Tests and verification (automated)

For each milestone agent must produce tests and run them:

* Unit tests (`pytest`) for each service.
* Integration smoke:

  * Insight → create synthetic Prometheus metric, call `/analyze`.
  * ETL → export + vectorize small sample.
  * Recommender → return recommendation for sample signal.
  * Orchestrator → full suggest→dry-run→approve→execute sequence with a safe playbook (`backup-verify` or `requeue-job`).

Agent records outputs in `/reports/logs/B.<milestone>.log` and summary in `/reports/B.<milestone>.md`.

---

## CI / CD hooks

Agent must add/update GitHub Actions workflows:

* `.github/workflows/B.insight-ci.yaml` — run tests, build docker image, push to registry (optional), run smoke integration.
* Add manual `deploy-prod` gate for orchestrator images.
* Include cosign signing step and trivy scan stage (use existing pipeline templates).

---

## Acceptance Criteria (Phase B MVP)

* Insight Engine returns useful signals and stores them.
* ETL pipeline produces vectors and inserts into vector DB (or local store).
* Recommender returns plausible playbook recommendations.
* Orchestrator performs full safe flow and records audit.
* BYOC connector can register a cluster and heartbeat.
* Minimal UI works and can approve/trigger runs.
* All policy docs created and policies enforced.
* Tests passing and `/reports/PhaseB_ Results.md` produced.

---

## Helper stubs to create now (agent must create if missing)

Agent must create minimal stubs to avoid blocking:

* `services/insight-engine/main.py` (simple FastAPI server)
* `services/etl/export_runs/export_to_jsonl.py`
* `services/etl/vectorize/vectorize.py` (calls OpenAI or fallback)
* `services/recommender/main.py` (FastAPI)
* `services/orchestrator/main.py` (FastAPI)
* `services/connector/agent.py` (registration heartbeat)
* `ui/neuralops/pages/index.js` (simple React page)
* `docs/policies/*.md` (safety, data redaction, approval)
* `infra/helm/*` (helm values placeholders)
* `reports/B.*.md` templates



```


```

---

## Deliverables (final)

* `/reports/PhaseB_Results.md` (summary)
* `/reports/B.*.md` for each milestone
* PRs per milestone + branch `prod-feature/B.complete` (meta)
* `docs/policies/*.md` (safety, data, approval)
* Helm charts and manifests for services
* CI workflows for tests and smoke runs

---

## Final notes

* Keep changes small and PR-chunked by milestone.
* Maintain strict audit logging for every automated action.
* If you want, I can now generate the actual starter code stubs (FastAPI templates, minimal vectorize script, Prom metrics exporters, and simple Next.js UI) in one message. Say “generate stubs” and I will output all files ready to paste.
