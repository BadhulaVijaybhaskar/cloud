# `/docs/Phase_F_Backend_Wiring.md`

**Agent-ready** plan to convert Launchpad UI from static → fully live by wiring backend services, realtime, AI, auth, storage, and marketplace. Agent runs autonomously. Drop this file in repo and run.

---

## Purpose

Make all Launchpad pages dynamic and connected to ATOM services. Provide real API contracts, stubs, tests, simulation fallbacks, security checks, and reporting. Works with `SIMULATION_MODE=true` when infra missing.

---

## Environment (required)

```
POSTGRES_DSN
VAULT_ADDR
MINIO_ENDPOINT
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
PROM_URL
KAFKA_URL or REDIS_URL
OPENAI_KEY (optional)
COSIGN_KEY_PATH (optional)
SIMULATION_MODE=true|false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
GIT_AUTHOR_NAME
GIT_AUTHOR_EMAIL
```

---

## Pre-run (one-time)

```bash
# create folders
mkdir -p services/launchpad-backend services/data-api services/auth-api services/storage-api \
  services/runtime-deploy services/realtime-bridge services/ai-proxy services/metrics-proxy \
  infra/helm/launchpad infra/helm/data-api tests/integration reports/logs
git add . && git commit -m "chore: create Phase F backend wiring dirs"
```

---

## High-level flow & gateway

* `ui/*` calls go to `launchpad-backend` (port `8001`) which proxies to internal microservices or simulation mocks.
* `launchpad-backend` handles auth, JWT injection, tenant routing, rate limits, WAF hooks.
* Components to implement:

  * `services/launchpad-backend/` — API gateway + mocking switch
  * `services/data-api/` — SQL run, tables, schema endpoints
  * `services/auth-api/` — user, roles, policy dry-run, login
  * `services/storage-api/` — MinIO wrapper (signed URLs, list, upload)
  * `services/runtime-deploy/` — WPK pack/sign/deploy API
  * `services/realtime-bridge/` — WebSocket → Kafka/Redis bridge
  * `services/metrics-proxy/` — Prometheus query proxy
  * `services/ai-proxy/` — Ask ATOM AI proxy for SQL suggestions and query AI
  * `services/logs-api/` — Loki query wrapper for UI logs

Ports:

* Gateway: `8001`
* Data API: `8011`
* Auth API: `8012`
* Storage API: `8013`
* Runtime: `8014`
* Realtime WS: `8015`
* Metrics proxy: `8016`
* AI proxy: `8017`
* Logs API: `8018`

All services expose `/health` and `/metrics`.

---

## Files to create (exact paths)

```
services/launchpad-backend/main.py
services/launchpad-backend/requirements.txt
services/launchpad-backend/Dockerfile
services/data-api/main.py
services/data-api/migrations/001_init.sql
services/auth-api/main.py
services/storage-api/main.py
services/runtime-deploy/main.py
services/realtime-bridge/main.py
services/metrics-proxy/main.py
services/ai-proxy/main.py
services/logs-api/main.py
infra/helm/launchpad/chart.yaml
tests/integration/test_endpoints.py
reports/F.backend_wiring_summary.md
reports/logs/F.backend_tests.log
```

---

## API Contracts (canonical)

### Gateway (launchpad-backend)

* `GET /health` → `{status:"ok", env:"SIM"|"LIVE"}`
* `POST /auth/login` → `{token:JWT}`
* Proxy routes:

  * `/api/data/query` → POST `{sql}` → forwards to data-api
  * `/api/data/tables` → GET → data-api
  * `/api/auth/users` → GET/POST → auth-api
  * `/api/policies` → GET/POST → auth-api
  * `/api/storage/buckets` → GET → storage-api
  * `/api/storage/signed-url` → POST `{path, method}` → storage-api
  * `/api/wpk/pack` → POST `{wpk}` → runtime-deploy
  * `/api/wpk/sign` → POST `{artifact}` → runtime-deploy (calls cosign via Vault)
  * `/api/wpk/deploy` → POST `{artifact_id}` → runtime-deploy
  * `/ws/realtime` → WebSocket endpoint → realtime-bridge
  * `/api/metrics/query` → POST `{query}` → metrics-proxy
  * `/api/ai/sql/suggest` → POST `{context}` → ai-proxy
  * `/api/logs/query` → POST `{query}` → logs-api

Gateway responsibilities:

* JWT verification and tenant context propagation (`x-tenant-id`).
* Rate limiting and simple WAF rules (block suspicious payloads).
* Simulation mode: return mocks if `SIMULATION_MODE=true`.

### Data API (services/data-api)

* `POST /query` → run SQL against POSTGRES_DSN or sqlite fallback. Return rows+columns.
* `GET /tables` → list tables + schema.
* Runs migrations on start if DB reachable.

### Auth API

* `POST /login` → accept username/password (simulation fallback) return JWT with tenant claims.
* `GET /users` / `POST /users` → CRUD (persist to Postgres).
* `POST /policies/dryrun` → accept policy JSON and simulate enforcement on sample records.

### Storage API

* `GET /buckets` → list buckets from MinIO or filesystem mock `/data/buckets`
* `POST /signed-url` → return pre-signed URL for upload/download (MinIO SDK).
* `POST /object/delete` → delete object.

### Runtime Deploy

* `POST /wpk/pack` → accept WPK JSON → create tarball → store artifact metadata
* `POST /wpk/sign` → call Vault/Cosign to sign artifact (simulation allowed)
* `POST /wpk/deploy` → push to workflow-registry and call runtime agent `/execute`
* Emit Prometheus metrics: `wpk_pack_total`, `wpk_deploy_total`

### Realtime Bridge

* WebSocket accepts subscriptions `{topic:"naksha.telemetry"}` and streams messages
* In live mode connects to Kafka/Redis; in sim mode emits synthetic events
* Support publish: client `{"publish":{topic,msg}}`

### Metrics Proxy

* `POST /query` → run Prometheus HTTP API query (PROM_URL) and return timeseries JSON
* Cache common queries 5s

### AI Proxy

* `POST /sql/suggest` → call OpenAI/HF embeddings or internal Ask ATOM AI (if not available return canned suggestions)
* `POST /query-ai` → natural language → return SQL + explanation

### Logs API

* `POST /query` → query Loki or file-based logs and return matching entries
* Support `tail=true` via WebSocket for live log streaming

---

## Simulation behavior

If `SIMULATION_MODE=true` or a service env var missing:

* Return static JSON stored under `services/<svc>/mocks/`.
* Emit synthetic Prometheus metrics.
* For WPK sign, return `{"signed":true,"signature":"SIM-SIGN"}` and flag `BLOCKED` in report.

Agent must record which endpoints ran in simulation.

---

## Tests (integration)

Create `tests/integration/test_endpoints.py` covering:

* Gateway health
* Data query `SELECT 1`
* Auth login -> create user -> list users
* Storage signed URL generation
* WPK pack -> sign -> deploy (sim)
* WS connect to `/ws/realtime` subscribe + receive message
* AI proxy SQL suggestion basic call

Run with:

```bash
pytest -q tests/integration/test_endpoints.py
```

Save output to `/reports/logs/F.backend_tests.log`.

---

## Security & Policy Hooks (mandatory)

* All services must check `X-Request-ID` and `Authorization: Bearer <JWT>`.
* Gateway must enforce `Content-Type` and reject requests > 2MB by default.
* WPK deploy requires artifact signature verification. If cosign unavailable, mark BLOCKED and disallow live deploys (simulation only).
* All services must write audit events to `audit.log` (append-only) with: timestamp, actor, tenant, action, sha256 (if artifact).
* Services must expose `/metrics` for Prometheus.

---

## Observability

* Each service exposes `/metrics` and `/health`.
* Gateway pushes basic metrics to Prometheus via `prometheus_client`.
* Logs go to `reports/logs/<service>.log` during agent run; prefer writing to `/var/log/atom/<service>.log` if available.

---

## Acceptance Criteria (Phase F backend wiring complete)

* Gateway `GET /health` returns ok and env mode.
* `POST /api/data/query` runs `SELECT 1` and returns `[[1]]`.
* Auth login returns JWT and `GET /api/users` returns created user.
* Storage signed URL works (simulation ok).
* `POST /api/wpk/pack` → `sign` → `deploy` run end-to-end in sim and produce audit entries.
* WebSocket `/ws/realtime` can subscribe and receive at least one message.
* AI `/api/ai/sql/suggest` returns suggestion text (sim allowed).
* Integration tests pass (or failures captured in logs) and report created: `/reports/F.backend_wiring_summary.md`.

---

## Report content (agent must produce `/reports/F.backend_wiring_summary.md`)

* Branch name & commit SHA
* Environment variables present / missing
* Tests run + pass/fail summary
* Verification outputs (curl responses, sample JSON)
* List of created files and directories
* Blocked items (cosign, Vault, external keys) if any
* `/reports/logs/F.backend_tests.log` attached

---

## Branching / CI / PR

For the agent, follow this exact sequence for the whole wiring task:

1. `git checkout -b prod-feature/F.backend-wiring`
2. Add files, tests, run `pytest`
3. `mkdir -p reports/logs`
4. Save test logs
5. `git add . && git commit -m "feat(F): backend wiring for Launchpad UI"`
6. `git push origin prod-feature/F.backend-wiring`
7. Create PR using `gh pr create --title "feat(F): backend wiring" --body-file reports/F.backend_wiring_summary.md` (if `gh` not available leave branch)

Agent must not push secrets. Use environment variables only.

---

## Runtime commands (for verification)

Start services (agent must start them locally in order or use docker-compose if available):

```bash
# run gateway
uvicorn services.launchpad-backend.main:app --host 0.0.0.0 --port 8001 &

# run dependent services
uvicorn services.data-api.main:app --port 8011 &
uvicorn services.auth-api.main:app --port 8012 &
uvicorn services.storage-api.main:app --port 8013 &
uvicorn services.runtime-deploy.main:app --port 8014 &
uvicorn services.realtime-bridge.main:app --port 8015 &
uvicorn services.metrics-proxy.main:app --port 8016 &
uvicorn services.ai-proxy.main:app --port 8017 &
uvicorn services.logs-api.main:app --port 8018 &
```

Run integration tests:

```bash
pytest -q tests/integration/test_endpoints.py > /reports/logs/F.backend_tests.log 2>&1 || true
```

Run quick manual checks (agent must capture output):

```bash
curl -s http://localhost:8001/health > /reports/F.gateway_health.json
curl -s -X POST http://localhost:8001/api/data/query -H "Content-Type:application/json" -d '{"sql":"SELECT 1"}' > /reports/F.query_out.json
python -c "import websocket, json; print('ws-test')"
```

---

## Failure handling & resilience

* If `POSTGRES_DSN` unreachable, data-api falls back to sqlite file under `/tmp/atom_sim.db` and notes fallback in report.
* If `MINIO` unreachable, storage-api uses local folder `/tmp/atom_buckets`.
* If `PROM_URL` missing, metrics-proxy serves synthetic series.
* If Kafka/Redis unreachable, realtime-bridge serves synthetic heartbeat messages.
* Agent must mark each fallback as `BLOCKED` in report and include remediation steps.

---

## Deliverables (on success)

* All service folders with code + tests
* Integration test logs under `/reports/logs/`
* `/reports/F.backend_wiring_summary.md` with verification artifacts
* Branch `prod-feature/F.backend-wiring` and PR ready

---

## Notes for human reviewer

* Provide Vault/Cosign test credentials securely if you want real sign/deploy flows. Do not commit credentials to git.
* To go live, run services in k8s with Helm charts in `infra/helm/*` after verifying locally.
* After wiring, proceed to UI changes: swap `NEXT_PUBLIC_API_BASE_URL` to gateway and enable live features.


