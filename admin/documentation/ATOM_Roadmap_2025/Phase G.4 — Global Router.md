Proceeding. Below is the **agent-ready `.md`** for **Phase G.4 — Global Router**. Drop it at `/docs/Phase_G.4_Global_Router_Agent.md` and hand to your ATOM agent. It is self-contained, enforces P1–P7, supports simulation mode, and contains prechecks, verification, and reporting instructions. No CI/gh automation.

```markdown
# Phase G.4 — Global Router (Agent-Ready Build Plan)

**Goal**  
Implement geo-aware intelligent routing, QoS balancing, and failover routing for ATOM Cloud. Provide per-tenant routing policies, region affinity, health-based routing, and throttling/QoS controls. Support simulation fallback.

**Version target:** v7.3.0-phaseG.4  
**Branch prefix (local):** `prod-feature/G.4.<task>`  
**Mode:** Autonomous / Simulation fallback ready

---

## Environment variables (agent reads)
```

GLOBAL_REGISTRY_URL
ROUTER_BIND_ADDR        # e.g. 0.0.0.0:8601
PRIMARY_REGION
SECONDARY_REGIONS       # comma-separated
PROM_URL
VAULT_ADDR
COSIGN_KEY_PATH
SIMULATION_MODE
MAX_P95_LATENCY_MS      # default 500
ROUTER_AUTH_TOKEN
GEOIP_DB_PATH

```
If critical vars missing agent sets `SIMULATION_MODE=true` and records missing items.

---

## Policies enforced (P1–P7)
* P1 Data Privacy — route metadata only, strip PII from logs.
* P2 Secrets & Signing — routing policy updates require cosign-signed manifest.
* P3 Execution Safety — failover/manual approval required for production promotions.
* P4 Observability — each router exposes `/health` and `/metrics`.
* P5 Multi-Tenancy — tenant routing isolation and namespace-based policies.
* P6 Performance Budget — p95 latency SLO enforced per routing decision.
* P7 Resilience & Recovery — automatic rollbacks on degraded region health.

---

## High-level tasks (G.4.1 → G.4.5)
| ID | Task | Goal |
|---:|------|------|
| G.4.1 | Router Core Service | Routing logic, policy engine, API |
| G.4.2 | Health & Telemetry Adapter | Aggregate health from regions, compute scores |
| G.4.3 | GeoIP & Affinity Module | Geo lookup, latency estimation, nearest-region logic |
| G.4.4 | QoS & Throttling Engine | Rate limits, weighted routing, tenant quotas |
| G.4.5 | Policy UI / Policy Sync API | Accept signed routing policies, versioning, audits |

---

## Files & directories to create (exact)
```

services/global-router/
services/router-health/
services/geo-affinity/
services/qos-engine/
services/router-policy/
infra/helm/global-router/chart.yaml
infra/ips/geoip/ (place GEOIP DB or mock)
tests/integration/test_G.4_end2end.py
docs/policies/router_policy.md
reports/

```
Each `services/*` must contain: `main.py`, `requirements.txt`, `Dockerfile`, `config.example.yaml`, `tests/`, `/metrics` hooks.

---

## Task details

### G.4.1 — Router Core Service
**Local branch:** `prod-feature/G.4.1-router-core`  
**Files**
```

services/global-router/main.py
services/global-router/policy_engine.py
services/global-router/storage.py
services/global-router/tests/test_core.py
reports/G.4.1_router_core.md

```
**Endpoints**
* `POST /route` — accepts `{tenant_id, path, method, headers, client_ip}` returns `{region, upstream_url, reason, trace_id}`
* `POST /policy/apply` — accept cosign-signed policy manifest (P2)
* `GET /policy/{id}` — policy status
* `GET /health`, `GET /metrics`

**Behavior**
* Evaluate tenant policy, geo affinity, health score, QoS budget.
* Enforce P5 tenant isolation.
* Log routing decision with trace_id and redacted metadata.

**Verification**
```

pytest -q services/global-router/tests/test_core.py > /reports/logs/G.4.1.log 2>&1 || true
curl -s -X POST [http://localhost:8601/route](http://localhost:8601/route) -d '{"tenant_id":"t1","path":"/api","client_ip":"1.2.3.4"}' -H "Content-Type:application/json" > /reports/G.4.1_route.json || true

```

---

### G.4.2 — Health & Telemetry Adapter
**Branch:** `prod-feature/G.4.2-health-adapter`  
**Files**
```

services/router-health/main.py
services/router-health/aggregator.py
services/router-health/tests/test_health.py
reports/G.4.2_health_adapter.md

```
**Behavior**
* Poll region `/health` and Prometheus metrics.
* Compute `region_score` combining p95 latency, error rate, capacity.
* Expose `/metrics` and `/regions` with scores.

**Verification**
```

pytest -q services/router-health/tests/test_health.py > /reports/logs/G.4.2.log 2>&1 || true
curl -s [http://localhost:8602/regions](http://localhost:8602/regions) > /reports/G.4.2_regions.json || true

```

---

### G.4.3 — GeoIP & Affinity Module
**Branch:** `prod-feature/G.4.3-geo-affinity`  
**Files**
```

services/geo-affinity/main.py
services/geo-affinity/geoip_lookup.py
services/geo-affinity/tests/test_geo.py
reports/G.4.3_geo_affinity.md

```
**Behavior**
* Use GEOIP_DB_PATH or mock DB to map client IP to region.
* Provide nearest-region ranking and estimated RTT (simulated based on distance).
* Offer override per tenant (policy-based affinity).

**Verification**
```

pytest -q services/geo-affinity/tests/test_geo.py > /reports/logs/G.4.3.log 2>&1 || true
curl -s [http://localhost:8603/affinity?ip=1.2.3.4](http://localhost:8603/affinity?ip=1.2.3.4) > /reports/G.4.3_affinity.json || true

```

---

### G.4.4 — QoS & Throttling Engine
**Branch:** `prod-feature/G.4.4-qos-engine`  
**Files**
```

services/qos-engine/main.py
services/qos-engine/limits.py
services/qos-engine/tests/test_qos.py
reports/G.4.4_qos_engine.md

```
**Behavior**
* Maintain tenant quotas, rate-limits, burst allowances.
* Weighted routing decisions under load.
* Circuit-breaker for unhealthy upstreams.

**Verification**
```

pytest -q services/qos-engine/tests/test_qos.py > /reports/logs/G.4.4.log 2>&1 || true
curl -s [http://localhost:8604/health](http://localhost:8604/health) > /reports/G.4.4_health.json || true

```

---

### G.4.5 — Policy UI / Policy Sync API
**Branch:** `prod-feature/G.4.5-policy-ui`  
**Files**
```

services/router-policy/main.py
services/router-policy/ui_stub.md
docs/policies/router_policy.md
services/router-policy/tests/test_policy_apply.py
reports/G.4.5_policy_ui.md

```
**Behavior**
* Accept policy manifests signed with cosign. Validate signature.
* Versioned policies with audit trail and `latest` pointer.
* Dry-run apply mode and automatic validation against P1–P7.

**Verification**
```

pytest -q services/router-policy/tests/test_policy_apply.py > /reports/logs/G.4.5.log 2>&1 || true
curl -s -X POST [http://localhost:8605/policy/apply](http://localhost:8605/policy/apply) -d @tests/sample_signed_policy.json -H "Content-Type:application/json" > /reports/G.4.5_apply.json || true

```

---

## Integration test (end-to-end)
Create `tests/integration/test_G.4_end2end.py` that:
* Starts (or pings) services.
* Posts `/route` requests under various simulated region health states.
* Applies a signed policy (or simulation).
* Validates routing decisions obey policy, geo, QoS, and region score.

Run:
```

pytest -q tests/integration/test_G.4_end2end.py > /reports/logs/G.4_end2end.log 2>&1 || true

```

---

## Precheck (agent-run)
Agent must run precheck and write `/reports/G.4_precheck.json`:
```

mkdir -p reports/logs
python - <<'PY' > /reports/G.4_precheck.json 2>&1
import os,json
r={}
for k in ["GLOBAL_REGISTRY_URL","GEOIP_DB_PATH","PROM_URL","VAULT_ADDR"]:
r[k]= "SET" if os.getenv(k) else "MISSING"
r["SIMULATION_MODE"]= os.getenv("SIMULATION_MODE","true")

# decision logic

if r["GLOBAL_REGISTRY_URL"]!="MISSING" or r["SIMULATION_MODE"]=="true":
r["decision"]="PROCEED" if r["GLOBAL_REGISTRY_URL"]!="MISSING" else "PROCEED_SIMULATION"
else:
r["decision"]="BLOCK"
print(json.dumps(r,indent=2))
PY

```
If `decision == BLOCK` create `/reports/G.4_precheck_block.txt` and stop.

---

## Metrics & Observability
* All services must expose Prometheus metrics.
* Recommended metrics: `router_requests_total{tenant,phase}`, `region_score`, `qos_rejections_total{tenant}`, `policy_applies_total`.
* Sample metric snapshot saved to `/reports/G.4_metrics_sample.txt` via `/metrics` curl.

---

## Security & Logging
* Never log secrets. Replace with `<REDACTED>`.
* Policy applies must record `applier`, `signature_sha256`, `timestamp`.
* Routing logs record `trace_id`, `tenant_id`, `region`, `reason`, `latency_ms` (no PII).
* Audit entries hashed and stored; include SHA256 ref in reports.

---

## Reports to produce (per task)
* `/reports/G.4.1_router_core.md`
* `/reports/G.4.2_health_adapter.md`
* `/reports/G.4.3_geo_affinity.md`
* `/reports/G.4.4_qos_engine.md`
* `/reports/G.4.5_policy_ui.md`
* `/reports/PhaseG.4_Snapshot.json`
* `/reports/logs/G.4.*.log`

Each report must include: branch & commit SHA, SIMULATION_MODE status, test outputs, verification outputs, policy pass/block table, and blockers.

---

## Acceptance criteria
* `/route` returns expected region decision for sample inputs.
* Policy apply requires cosign signature (or simulated sign) when non-sim.
* Health adapter produces region scores used by router.
* QoS engine enforces tenant limits under simulated load.
* All `/health` endpoints respond 200.

---

## Failure handling
* Missing GEOIP DB → use simple IP→region map simulation.
* Prometheus unreachable → health adapter uses region `/health` polls.
* Cosign missing → policy apply allowed only in simulation mode; report BLOCKED for P2.
* All failures logged to `/reports/logs/` and marked in reports as `BLOCKED` where appropriate.

---

## Finalization
When tasks complete or simulate successfully:
1. Run `python scripts/generate_phase_snapshot.py` to create `/reports/PhaseG.4_Snapshot.json`.
2. Commit local branches with messages `feat(G.4.x): <short> implemented (agent)`.
3. Do not push or create PRs automatically. Leave manual merge instructions in `/reports/PhaseG.4_final_summary.md`.
4. Recommend tag `v7.3.0-phaseG.4`.

---

## Embedded agent prompt
```

You are the ATOM coding agent. Execute Phase G.4 per this file. Run precheck. If infra missing set SIMULATION_MODE=true. Implement G.4.1→G.4.5, run tests, write reports, and generate PhaseG.4_Snapshot.json. Do not push branches or open PRs. Do not log secrets. Mark blocked items in reports and continue simulation where possible.

```

---  
End of Phase G.4 agent file.
```

