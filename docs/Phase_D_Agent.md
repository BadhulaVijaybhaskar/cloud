# Phase D — Deep Intelligence & Autonomous Ops

Agent-ready single-file plan with all dependent stubs, policy rules, and exact execution steps.

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
tests/insight_stream/test_ingest.py
reports/D.1_insight_stream.md
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

## Verification commands (agent must run)
```bash
python -m pytest tests/insight_stream/test_ingest.py -q > /reports/logs/D.1_tests.log 2>&1 || true
curl -sS http://localhost:8010/health > /reports/D.1_health.json || true
curl -sS -X POST http://localhost:8010/ingest -H "Content-Type: application/json" -d '{"m":1}' || true
curl -sS http://localhost:8010/metrics | head -n 20 > /reports/D.1_metrics.txt || true
```

## Report
`/reports/D.1_insight_stream.md` must include health output, test results, backend chosen and any BLOCKED infra.

---

# Task D.2 — Autonomous Agent Framework (autonomous-agent)

## Objective
Create agent runtime that uses WPK registry + LangGraph-style graph reasoning to observe→decide→act.

## Branch
`prod-feature/D.2-autonomous-agent`

## Files to create
```
services/autonomous-agent/main.py
services/autonomous-agent/agentspec.yaml
services/autonomous-agent/requirements.txt
services/autonomous-agent/Dockerfile
tests/autonomous_agent/test_agent_flow.py
reports/D.2_agent_framework.md
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

@app.post("/agent/run")
def run(payload: dict, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    background_tasks.add_task(process, run_id, payload)
    return {"run_id": run_id}

def process(run_id, payload):
    RUNS.inc()
    # observe -> decide -> act stages (simulate)
    import json, os, time
    os.makedirs("/tmp/agent_runs", exist_ok=True)
    result = {"id": run_id, "payload": payload, "result": "simulated", "ts": time.time()}
    with open(f"/tmp/agent_runs/{run_id}.json", "w") as f:
        json.dump(result, f)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    from prometheus_client import generate_latest
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8020)
```

## Tests & verification
* `pytest -q tests/autonomous_agent/test_agent_flow.py`
* `curl -X POST http://localhost:8020/agent/run -d '{"signal":"s"}'`

## Report
`/reports/D.2_agent_framework.md` include run logs and proof that run files exist under `/tmp/agent_runs/`.

---

# Task D.3 — Continuous Learning Loop (cll-trainer)

## Objective
Create online retraining pipeline that consumes run history and streaming signals to produce model versions.

## Branch
`prod-feature/D.3-cll-trainer`

## Files
```
services/cll-trainer/train.py
services/cll-trainer/requirements.txt
services/cll-trainer/Dockerfile
tests/cll/test_train.py
reports/D.3_cll_trainer.md
```

## Minimal train.py stub
```python
# train.py: reads /tmp/agent_runs for simulation, writes model_versions.json
import json, os, uuid, time

def main():
    input_path = os.getenv("CLL_INPUT", "/tmp/agent_runs")
    out = {"model_id": str(uuid.uuid4()), "created": time.time(), "score": 0.5}
    os.makedirs("/tmp/cll_models", exist_ok=True)
    with open("/tmp/cll_models/" + out["model_id"] + ".json","w") as f:
        json.dump(out,f)
    print(json.dumps(out))
    return out

if __name__ == "__main__":
    main()
```

## Verification
* Run `python services/cll-trainer/train.py` and confirm `/tmp/cll_models/*.json` exists.
* `pytest tests/cll/test_train.py`

## Report
`/reports/D.3_cll_trainer.md` include model file listing and metrics.

---

# Task D.4 — Federated Ops & Edge Compute (federation-hub + edge-node)

## Objective
Add simple federation API and edge-agent that can register and receive signed WPK triggers.

## Branch
`prod-feature/D.4-federation`

## Files
```
services/federation-hub/main.py
services/edge-node/agent.py
tests/federation/test_registration.py
reports/D.4_federation.md
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
Implement service that schedules fault injections and validates autonomous recovery via agents.

## Branch
`prod-feature/D.5-chaos`

## Files
```
services/chaos-orchestrator/main.py
services/chaos-orchestrator/requirements.txt
tests/chaos/test_injection.py
reports/D.5_chaos.md
```

## Verification
* Schedule chaos event, verify agent response

## Report
`/reports/D.5_chaos.md` include chaos logs and recovery validation.

---

# Task D.6 — Production Deployment Pipeline (deploy-pipeline)

## Objective
Create deployment automation with GitOps integration and rollback capabilities.

## Branch
`prod-feature/D.6-deploy-pipeline`

## Files
```
services/deploy-pipeline/main.py
services/deploy-pipeline/requirements.txt
infra/gitops/deployment.yaml
tests/deploy/test_pipeline.py
reports/D.6_deploy_pipeline.md
```

## Verification
* Test deployment simulation
* Verify rollback capability

## Report
`/reports/D.6_deploy_pipeline.md` include deployment logs and status.

---

# Finalization

After D.6, run:
1. `scripts/generate_phase_snapshot.py D`
2. Create branch `prod-review/PhaseD-Finalization`
3. Tag `v4.0.0-phaseD`
4. Push all branches and tags