Phase D — Deep Intelligence & Autonomous Ops
Agent-ready single-file plan with all dependent stubs, policy rules, and exact execution steps. Drop this file at `/docs/Phase_D_Agent.md` and give it to your coding agent. The agent must run tasks sequentially, commit each task to branch `prod-feature/D.<task>` and open a PR. Each task section contains files to create, exact endpoints, test commands, verification commands, report paths, and branch/PR instructions. Safety and policy enforcement are embedded.

# Phase D — Agent-run Implementation (one-file)

## Overview

Goal: build autonomous ops stack (D.1 → D.6). Each task runs sequentially. Use simulation mode when external infra (Kafka, Vault, Prometheus, cosign) is unavailable; document BLOCKED items in reports. Produce reports under `/reports/` for each task. All created files must be committed and pushed.

---

# Task D.1 — Real-Time Intelligence Layer (insight-stream)

## Objective

Add streaming ingestion service with switchable backends (Kafka or Redis Streams) and a simulation mode.

## Branch

`prod-feature/D.1-insight-stream`

## Files to create (exact paths)

```
services/insight-stream/main.py
services/insight-stream/requirements.txt
services/insight-stream/Dockerfile
services/insight-stream/config.example.yaml
infra/helm/insight-stream/values.yaml
infra/helm/insight-stream/chart.yaml
reports/D.1_insight_stream.md
tests/insight_stream/test_ingest.py
mocks/kafka_mock.py
```

## File contents (stubs) — create verbatim

### services/insight-stream/requirements.txt

```
fastapi
uvicorn[standard]
aiokafka
redis
pydantic
prometheus-client
pyyaml
```

### services/insight-stream/config.example.yaml

```yaml
ingestion:
  backend: kafka          # kafka | redis | mock
  kafka:
    bootstrap_servers: "localhost:9092"
    topic: "naksha.telemetry"
  redis:
    url: "redis://localhost:6379/0"
app:
  port: 8010
metrics:
  enabled: true
```

### services/insight-stream/main.py

```python
from fastapi import FastAPI, BackgroundTasks
from prometheus_client import Counter, generate_latest
import os, yaml, asyncio

app = FastAPI()
INGESTED = Counter("insight_ingested_total", "ingested messages")

# load config
cfg_path = os.getenv("INSIGHT_CONFIG", "services/insight-stream/config.example.yaml")
with open(cfg_path) as f:
    cfg = yaml.safe_load(f)

BACKEND = cfg.get("ingestion", {}).get("backend", "mock")

@app.get("/health")
def health():
    return {"status": "ok", "backend": BACKEND}

@app.get("/metrics")
def metrics():
    return generate_latest()

@app.post("/ingest")
async def ingest(payload: dict, background_tasks: BackgroundTasks):
    # quick handler: increment counter and enqueue to backend
    INGESTED.inc()
    background_tasks.add_task(process, payload)
    return {"status": "accepted"}

async def process(payload):
    # push to backend or simulate
    if BACKEND == "mock":
        await asyncio.sleep(0.01)
        return True
    # real backend hooks left for implementation

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.insight-stream.main:app", host="0.0.0.0", port=8010, log_level="info")
```

### mocks/kafka_mock.py

```python
# simple producer mock for local testing
import time, json
def produce(topic, msg):
    with open("/tmp/kafka_mock.log","a") as f:
        f.write(f"{time.time()} {topic} {json.dumps(msg)}\n")
```

### services/insight-stream/Dockerfile

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
```

## Endpoints to implement

* `GET /health`
* `POST /ingest` — accepts JSON telemetry
* `GET /metrics` — Prometheus format

## Tests

`pytest -q tests/insight_stream/test_ingest.py`
Test should POST sample payload and check `/metrics` increments. Provide mock test that passes in simulation.

## Verification commands (agent must run)

```bash
python -m pytest tests/insight_stream/test_ingest.py -q > /reports/logs/D.1_tests.log 2>&1 || true
curl -sS http://localhost:8010/health > /reports/D.1_health.json || true
curl -sS -X POST http://localhost:8010/ingest -H "Content-Type: application/json" -d '{"m":1}' || true
curl -sS http://localhost:8010/metrics | head -n 20 > /reports/D.1_metrics.txt || true
```

## Report

`/reports/D.1_insight_stream.md` must include:

* health output
* test results
* backend chosen and any BLOCKED infra

---

# Task D.2 — Autonomous Agent Framework (autonomous-agent)

## Objective

Create agent runtime that uses WPK registry + LangGraph-style graph reasoning to observe→decide→act. Must support plugins for "observe" sources and "act" adapters. Include a simulation mode.

## Branch

`prod-feature/D.2-autonomous-agent`

## Files to create

```
services/autonomous-agent/main.py
services/autonomous-agent/agentspec.yaml
services/autonomous-agent/requirements.txt
services/autonomous-agent/Dockerfile
services/autonomous-agent/plugins/observe_prometheus.py
services/autonomous-agent/plugins/act_k8s.py
reports/D.2_agent_framework.md
tests/autonomous_agent/test_agent_flow.py
```

## Key endpoints

* `POST /agent/run` — submit signal id or telemetry to run agent cycle
* `GET /agent/status/{id}` — status

## Minimal main.py stub (create)

```python
from fastapi import FastAPI, BackgroundTasks
import yaml, os, uuid, logging
from prometheus_client import Counter

app = FastAPI()
RUNS = Counter("autonomous_agent_runs_total", "Total runs")

cfg = yaml.safe_load(open("services/autonomous-agent/agentspec.yaml"))
@app.post("/agent/run")
def run(payload: dict, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    background_tasks.add_task(process, run_id, payload)
    return {"run_id": run_id}

def process(run_id, payload):
    RUNS.inc()
    # observe -> decide -> act stages (simulate)
    # write run result to /tmp/agent_runs/{run_id}.json
    import json, os, time
    os.makedirs("/tmp/agent_runs", exist_ok=True)
    result = {"id": run_id, "payload": payload, "result": "simulated", "ts": time.time()}
    with open(f"/tmp/agent_runs/{run_id}.json", "w") as f:
        json.dump(result, f)
```

## Tests & verification

* `pytest -q tests/autonomous_agent/test_agent_flow.py`
* `curl -X POST http://localhost:8020/agent/run -d '{"signal":"s"}'`

## Report

`/reports/D.2_agent_framework.md` include run logs and proof that run files exist under `/tmp/agent_runs/`.

---

# Task D.3 — Continuous Learning Loop (cll-trainer)

## Objective

Create online retraining pipeline that consumes run history and streaming signals to produce model versions and register them in `model_versions` table.

## Branch

`prod-feature/D.3-cll-trainer`

## Files

```
services/cll-trainer/train.py
services/cll-trainer/requirements.txt
services/cll-trainer/Dockerfile
services/cll-trainer/model_store.py
infra/sql/003_create_model_versions.sql
reports/D.3_cll_trainer.md
tests/cll/test_train.py
```

## Minimal train.py stub

```python
# train.py: reads /data/export_runs.jsonl or /tmp/agent_runs for simulation, writes model_versions.json
import json, os, uuid, time
input_path = os.getenv("CLL_INPUT", "/tmp/agent_runs")
out = {"model_id": str(uuid.uuid4()), "created": time.time(), "score": 0.5}
os.makedirs("/tmp/cll_models", exist_ok=True)
with open("/tmp/cll_models/" + out["model_id"] + ".json","w") as f:
    json.dump(out,f)
print(out)
```

## Verification

* Run `python services/cll-trainer/train.py` and confirm `/tmp/cll_models/*.json` exists.
* `pytest tests/cll/test_train.py`

## Report

`/reports/D.3_cll_trainer.md` include model file listing and metrics.

---

# Task D.4 — Federated Ops & Edge Compute (federation-hub + edge-node)

## Objective

Add simple federation API and edge-agent that can register and receive signed WPK triggers. Use Vault token or simulation.

## Branch

`prod-feature/D.4-federation`

## Files

```
services/federation-hub/main.py
services/edge-node/agent.py
infra/helm/federation/chart.yaml
docs/policies/edge_security.md
reports/D.4_federation.md
tests/federation/test_registration.py
```

## Minimal behavior

* edge-node registers via `POST /federation/register` with JWT token (or sim)
* hub stores registration in `federation_registry.json`

## Verification

* Start hub, start edge-node (simulation), call register, verify entry exists.

## Report

`/reports/D.4_federation.md` include registry contents and security notes.

---

# Task D.5 — Global Resilience & Chaos Automation (chaos-orchestrator)

## Objective

Implement service that schedules fault injections (network pod kill, CPU spike simulated) and validates autonomous recovery via agents.

## Branch

`prod-feature/D.5-chaos`

## Files

```
services/chaos-orchestrator/main.py
services/chaos-orchestrator/chaos_specs.yaml
infra/helm/chaos/chart.yaml
reports/D.5_chaos_automation.md
tests/chaos/test_chaos_flow.py
```

## Minimal functions

* `POST /chaos/run` accepts `spec_id` and triggers simulated failure by calling runtime agent or k8s adapter (simulation mode)
* collect results and store in `/tmp/chaos_runs/*.json`

## Verification

* run `curl -X POST http://localhost:8030/chaos/run -d '{"spec":"kill-pod"}'`
* confirm `/tmp/chaos_runs/*.json` created and contains recovery outcome

## Report

`/reports/D.5_chaos_automation.md` include run output and agent recovery evidence.

---

# Task D.6 — Compliance & Policy Learning (policy-learner)

## Objective

Policy-learner ingests audit logs and human approvals to produce policy suggestions and a compliance matrix.

## Branch

`prod-feature/D.6-policy-learner`

## Files

```
services/policy-learner/main.py
services/policy-learner/requirements.txt
data/audits/sample_audit.jsonl
reports/D.6_policy_learning.md
tests/policy_learner/test_policy_suggest.py
docs/policies/policy_learning.md
```

## Minimal stub

* `POST /learn` ingest JSONL audits and output suggested policy JSON
* produce `/reports/D.6_policy_learning.md` summarizing suggested changes

## Verification

* `pytest tests/policy_learner/test_policy_suggest.py`
* `curl -X POST http://localhost:8040/learn -d @data/audits/sample_audit.jsonl`

## Report

`/reports/D.6_policy_learning.md` include suggested policy JSON.

---

# Cross-task required helper files & policies (create once)

## 1) /docs/policies/POLICIES.md (single canonical policy file)

Create `/docs/policies/POLICIES.md` with the following content verbatim.

```markdown
# Global Policies (enforced across Phase D)

P-1 Data Privacy
- No raw PII stored in model inputs.
- Streams must anonymize IPs and identifiers.
- Storage only stores aggregated features for training.

P-2 Secrets & Signing
- All secrets must be in Vault or injected at runtime via CSI.
- All WPKs and models must be signed with cosign.
- Edge agents must validate signatures before execution.

P-3 Execution Safety
- Default safety.mode = manual.
- Any WPK labelled `auto` must have `dry_run` pass and an approver recorded before execution.
- Orchestrator must record approver id, justification, and sha256 of before/after state.

P-4 Observability
- Each service must expose `/metrics` (Prometheus) and `/health`.
- Distributed tracing via OpenTelemetry (where available).

P-5 Multi-Tenancy
- Every request must carry tenant id in JWT.
- Postgres RLS or equivalent must enforce tenant isolation.

P-6 Performance Budget
- Agent actions must meet latency SLOs.
- Long-running jobs must be asynchronous with progress telemetry.

Enforcement:
- The registry validator, policy-learner, and CI checks must enforce these policies.
```

## 2) env file example `/env.example`

```
POSTGRES_DSN=sqlite:////tmp/phaseD.db
VAULT_ADDR=http://127.0.0.1:8200
COSIGN_KEY_PATH=/vault/secrets/cosign.key
KAFKA_URL=localhost:9092
SIMULATION_MODE=true
```

## 3) scripts/generate_phase_snapshot.py

Create `scripts/generate_phase_snapshot.py` that aggregates commit SHAs and report list.

```python
import json,subprocess,glob
snap = {}
snap["commit"] = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
snap["reports"] = glob.glob("reports/*.md")
print(json.dumps(snap, indent=2))
open("reports/PhaseD_Snapshot.json","w").write(json.dumps(snap,indent=2))
```

---

# Execution instructions (agent-run, sequential, exact commands)

Place these commands inside each task's branch commit process. Agent must follow these exact steps for each task in order D.1 → D.6.

For each task `<T>` (replace placeholders), agent must:

1. `git checkout -b prod-feature/D.<T>-<shortname>`
2. Create files listed in the task section, with content stubs provided in this document.
3. Run unit tests for that task:

   ```bash
   pytest -q tests/<task_dir> || true
   ```

   Save output:

   ```bash
   mkdir -p /reports/logs
   pytest -q tests/<task_dir> > /reports/logs/D.<T>_tests.log 2>&1 || true
   ```
4. Start the service locally (use uvicorn). Example:

   ```bash
   # example for insight-stream
   uvicorn services.insight-stream.main:app --host 0.0.0.0 --port 8010 &> /reports/logs/D.1_run.log &
   ```
5. Run verification commands (task-specific). Save all outputs under `/reports/`.
6. Populate `/reports/D.<T>_<shortname>.md` with:

   * health output
   * tests output snippet
   * verification commands output
   * list of created files and commit SHA
   * BLOCKED items (if external infra missing)
7. Commit and push:

   ```bash
   git add .
   git commit -m "feat(D.<T>): <shortname> - implemented (agent)"
   git push origin prod-feature/D.<T>-<shortname>
   gh pr create --title "feat(D.<T>): <shortname>" --body-file reports/D.<T>_<shortname>.md || true
   ```

   (If `gh` CLI missing, create PR manually or leave commit and branch.)
8. Move to next task.

---

# Finalization (after D.6)

Agent must run:

```bash
# run aggregation
python scripts/generate_phase_snapshot.py
git add reports/PhaseD_Snapshot.json
git commit -m "chore: PhaseD snapshot" || true
git push origin main
# create final PR
git checkout -b prod-review/PhaseD-Finalization
git merge --no-ff prod-feature/D.1-insight-stream -m "merge D.1" || true
git merge --no-ff prod-feature/D.2-autonomous-agent -m "merge D.2" || true
git merge --no-ff prod-feature/D.3-cll-trainer -m "merge D.3" || true
git merge --no-ff prod-feature/D.4-federation -m "merge D.4" || true
git merge --no-ff prod-feature/D.5-chaos -m "merge D.5" || true
git merge --no-ff prod-feature/D.6-policy-learner -m "merge D.6" || true
git push origin prod-review/PhaseD-Finalization
# tag
git tag -a v4.0.0-phaseD -m "phase D complete"
git push origin v4.0.0-phaseD
```

If merge conflicts occur, open issues and attach diffs to PR rather than force merging.

---


```

```

---

# Notes for the human operator

* Put Vault, Kafka, Redis, Prometheus, and cosign in place to convert simulation mode to live tests. If unavailable, reports must clearly mark BLOCKED items and the agent continues using simulation.
* Ensure GitHub token and `gh` CLI are available if agent must open PRs automatically.
* Review reports after each PR and approve merges with CI gating.

---

# Deliverables (what agent must leave in repo)

* `services/*` directories for D.1..D.6
* `infra/helm/*` stubs for each service
* `/docs/policies/POLICIES.md`
* `/env.example`
* `/scripts/generate_phase_snapshot.py`
* `/reports/D.1_insight_stream.md` ... `/reports/D.6_policy_learning.md`
* `/reports/PhaseD_Snapshot.json`
* Branches and PRs per task
* Tag `v4.0.0-phaseD`

---


