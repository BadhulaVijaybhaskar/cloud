Saved. Paste the block below into `/docs/Phase_A_Foundation.md` and give it to your agent.

````markdown
# Phase A — Foundation (Agent-ready)

**Duration:** 1–2 weeks (solo + AI agents)  
**Goal:** Capture LangGraph run history, provide a simple Insight Engine that emits anomaly signals, and wire registry storage to run-history so NeuralOps can learn.  
**Branch prefix:** `prod-feature/A-<task>`

---

## Context
Phase 0.5 (Plug-and-Play) is complete. Phase A builds the data and signals NeuralOps needs:
- Persist LangGraph workflow runs.
- Produce anomaly signals from Prometheus.
- Link registry entries to run history.

---

## Manual Pre-Run Setup (run once locally)
```bash
mkdir -p services/langgraph/hooks \
  services/insight-engine \
  infra/db/migrations \
  services/workflow-registry/storage \
  services/workflow-registry/tests \
  services/langgraph/tests \
  services/insight-engine/tests \
  reports/logs
git add . && git commit -m "chore: create Phase A directories"
````

---

## Environment variables (agent expects set)

```
POSTGRES_DSN
VAULT_ADDR
MILVUS_ENDPOINT
PROM_URL
OPENAI_KEY (optional)
KUBECONFIG
```

If `POSTGRES_DSN` is not set agent must fall back to sqlite for tests and record that in reports.

---

## Task A.1 — LangGraph run history (DB + emitter)

**Goal:** Persist every LangGraph workflow run into Postgres and optionally upsert an embedding for run outputs to Milvus.

**Files to create/modify**

```
infra/db/migrations/001_create_workflow_runs.sql
services/langgraph/hooks/run_logger.py
services/langgraph/requirements.txt
services/langgraph/tests/test_run_logger.py
reports/0A.1_run_logger.md
```

**DB migration (`001_create_workflow_runs.sql`)**

* Table `workflow_runs`:

  * `id` UUID PK
  * `wpk_id` text
  * `run_id` text
  * `inputs` jsonb
  * `outputs` jsonb
  * `status` text
  * `duration_ms` int
  * `node_logs` jsonb
  * `created_at` timestamptz default now()
  * `updated_at` timestamptz

**Implementation steps**

1. Add SQL migration file.
2. Implement `log_run(run_obj)` in `run_logger.py`:

   * Validate payload.
   * Insert row into `workflow_runs`.
   * If `OPENAI_KEY` present and `outputs.text` exists:

     * Generate embedding via OpenAI (or skip if key missing).
     * Upsert vector to Milvus (use `MILVUS_ENDPOINT`).
   * Return `run_id`.
3. Integrate hook: call `log_run` at LangGraph run completion (or provide documented mock hook to simulate).
4. Add unit test `test_run_logger.py` using sqlite fallback if `POSTGRES_DSN` unset.
5. Create report `/reports/0A.1_run_logger.md` with commands run and results.

**Acceptance Criteria**

* Migration applies.
* `log_run` inserts row and returns id.
* If `OPENAI_KEY` present, Milvus upsert executed.
* Report created.

**Verification**

```bash
psql "$POSTGRES_DSN" -c "\dt workflow_runs" || echo "psql unreachable"
python -m pytest services/langgraph/tests/test_run_logger.py -q
python -c "from services.langgraph.hooks.run_logger import log_run; print(log_run({'wpk_id':'test','run_id':'r1','inputs':{},'outputs':{'text':'ok'},'status':'completed','node_logs':[],'duration_ms':123}))"
```

**Branch/PR**

* Branch: `prod-feature/A.1-run-logger`
* Commit message: `langgraph: add run logger + migration`
* Report: `/reports/0A.1_run_logger.md`

---

## Task A.2 — Insight Engine stub

**Goal:** Small service to query Prometheus, compute basic anomaly heuristics (z-score / EWMA), and store signals in DB.

**Files to create**

```
infra/db/migrations/002_create_insight_signals.sql
services/insight-engine/server.py
services/insight-engine/requirements.txt
services/insight-engine/tests/test_signals.py
reports/0A.2_insight_engine.md
```

**DB migration (`002_create_insight_signals.sql`)**

* Table `insight_signals`:

  * `id` UUID PK
  * `metric` text
  * `value` double precision
  * `score` double precision
  * `hint` text
  * `created_at` timestamptz default now()

**Implementation steps**

1. Create migration file.
2. Implement FastAPI `server.py`:

   * `POST /probe` accepts `{ "query": "<promql>", "threshold": <num> }`.
   * Query Prometheus at `PROM_URL` for last N points.
   * Compute z-score (or EWMA). If score >= threshold create signal row.
   * `GET /signals` returns recent signals.
3. Add unit test that mocks Prometheus responses and asserts DB insert.
4. Write `/reports/0A.2_insight_engine.md`.

**Acceptance Criteria**

* `POST /probe` returns `{signal_id, score}` for anomalies.
* Signal row exists in DB.

**Verification**

```bash
python -m pytest services/insight-engine/tests/test_signals.py -q
curl -sX POST http://localhost:8001/probe -d '{"query":"up","threshold":2}' -H "Content-Type:application/json"
psql "$POSTGRES_DSN" -c "select * from insight_signals order by created_at desc limit 5;" || echo "psql unreachable"
```

**Branch/PR**

* Branch: `prod-feature/A.2-insight`
* Commit message: `insight: add probe endpoint and signal store`
* Report: `/reports/0A.2_insight_engine.md`

---

## Task A.3 — Wire Registry storage to run-history

**Goal:** Provide `GET /workflows/{id}/runs` in workflow-registry returning paginated run summaries. Ensure registry metadata links to latest run.

**Files to create/modify**

```
services/workflow-registry/server.py   # update endpoints
services/workflow-registry/storage/    # ensure usage
services/workflow-registry/tests/test_runs_endpoint.py
reports/0A.3_registry_runs.md
```

**Implementation steps**

1. Add endpoint `GET /workflows/{id}/runs?limit=20&page=1`.

   * Query `workflow_runs` by `wpk_id` and return list of `{run_id,status,duration_ms,created_at}`.
2. Ensure when `log_run` is called, registry `latest_run_id` is updated:

   * Preferred: single DB shared access update.
   * Alternative: runtime hook calls registry `POST /workflows/{id}/runs/notify` with run_id (registry persists mapping).
3. Add unit test for endpoint.
4. Document `/reports/0A.3_registry_runs.md`.

**Acceptance Criteria**

* Endpoint returns runs array.
* `latest_run_id` available in registry metadata after run.

**Verification**

```bash
curl -s http://localhost:8000/workflows/test-workflow/runs | jq .
python -m pytest services/workflow-registry/tests/test_runs_endpoint.py -q
psql "$POSTGRES_DSN" -c "select run_id from workflow_runs where wpk_id='test-workflow' order by created_at desc limit 1;" || echo "psql unreachable"
```

**Branch/PR**

* Branch: `prod-feature/A.3-registry-runs`
* Commit message: `registry: add runs endpoint + link to run-history`
* Report: `/reports/0A.3_registry_runs.md`

---

## Final Phase A checks & summary

**Run final checks**

```bash
python -m pytest -q
curl -s http://localhost:8001/signals | jq .
curl -s http://localhost:8000/workflows/test-workflow/runs | jq .
psql "$POSTGRES_DSN" -c "select count(*) from workflow_runs;" || echo "psql unreachable"
```

**Produce final summary**

* `/reports/Phase_A_summary.md` must list:

  * PR links for A.1, A.2, A.3
  * PASS/FAIL per task
  * Commands run and outputs (or links to logs)
  * Blockers and next steps (Phase B inputs)

---

## Safety & error handling

* If DB unreachable, use sqlite for tests and log fallback in report.
* If `OPENAI_KEY` missing skip embedding but log in `/reports/0A.1_run_logger.md`.
* On any failure capture `kubectl describe pod` and `kubectl logs` if relevant to `/reports/logs/A.x_<task>.log`.
* Do not modify files outside listed paths. If required changes occur, record and open PR.



---

```
