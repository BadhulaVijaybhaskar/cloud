Excellent.
Below is the **complete agent-ready `.md` build plan** for **Phase G.1 — Global Federation Infrastructure**, followed by its **dependency & policy file**.

Both are fully autonomous: drop them under `/docs/` and your agent (Amazon Q or ATOM Agent) can execute end-to-end without human supervision.

---

## **1️⃣ `/docs/Phase_G.1_Global_Federation_Agent.md`**

```markdown
# Phase G.1 — Global Federation Infrastructure (Agent-Ready Build Plan)

**Objective**  
Extend ATOM Cloud from a single-region deployment to a **multi-region, self-replicating, zero-trust federation**.  
Implements cross-region APIs, replication controllers, tenant synchronization, and fail-over orchestration.

**Version Target:** v7.0.0-phaseG.1  
**Branch Prefix:** `prod-feature/G.1.<task>`  
**Mode:** Autonomous / Simulation fallback ready

---

## 🧭 Phase Scope & Deliverables
1. Global Region Registry API  
2. Federation Sync Service (for cross-region DB replication)  
3. Edge Controller (geo-aware routing + failover)  
4. Tenant Replicator (per-org data mirror with RLS)  
5. Metrics Aggregator (global Prometheus bridge)  
6. Disaster Recovery Coordinator (backup validation + rebuild)  
7. Federation Policy Manager (secure membership + trust exchange)  

All modules enforce P1–P7 policies (see dependency file below).

---

## ⚙️ Environment Variables
```

GLOBAL_REGISTRY_URL
PRIMARY_REGION
SECONDARY_REGIONS
POSTGRES_DSN
REDIS_URL
VAULT_ADDR
COSIGN_KEY_PATH
SIMULATION_MODE
FEDERATION_TOKEN
PROM_URL
S3_ENDPOINT

```

If any critical var missing → agent sets `SIMULATION_MODE=true`.

---

## 🧩 Task List (G.1.1 → G.1.7)

| Task | Component | Goal |
|:--|:--|:--|
| G.1.1 | Region Registry | Register and track regions and status |
| G.1.2 | Federation Sync | Cross-region database replication controller |
| G.1.3 | Edge Controller | Geo routing + region fail-over logic |
| G.1.4 | Tenant Replicator | Tenant-scoped data mirror and consistency |
| G.1.5 | Metrics Aggregator | Merge Prometheus metrics from regions |
| G.1.6 | Disaster Recovery | Snapshot backup + rebuild validation |
| G.1.7 | Federation Policy Manager | Trust exchange + membership governance |

---

## 🧱 Example Task Spec (G.1.1 — Region Registry)

**Branch:** `prod-feature/G.1.1-region-registry`

**Files**
```

services/region-registry/main.py
services/region-registry/models.py
services/region-registry/tests/test_registry.py
infra/helm/region-registry/chart.yaml
reports/G.1.1_region_registry.md

````

**Endpoints**
| Method | Path | Purpose |
|:--|:--|:--|
| POST | /region/register | Register region info (name, url, keys) |
| GET | /region/list | List known regions |
| GET | /health | Service check |

**Policy hooks**
- P2 Secrets & Signing: region registration must be cosign-signed.  
- P3 Execution Safety: approver required for production additions.  

**Verification**
```bash
pytest -q services/region-registry/tests > /reports/logs/G.1.1.log 2>&1 || true
curl -s http://localhost:8401/region/list > /reports/G.1.1_list.json || true
````

---

## Execution Steps (Agent Sequence)

1. **Pre-check** → run `docs/compliance-precheck_G.1.md`; if `BLOCK` → halt, else continue (simulation if flagged).
2. For each task G.1.x:
    a. `git checkout -b prod-feature/G.1.x-<short>`
    b. Generate service files and helm chart per spec
    c. Run `pytest`; save logs to `/reports/logs/`
    d. Run verification curl commands
    e. Create report `/reports/G.1.x_<short>.md` with results + policy table
    f. Commit + PR:
     `bash
     git add . && git commit -m "feat(G.1.x): <short>" && git push origin prod-feature/G.1.x-<short>
     gh pr create --title "feat(G.1.x): <short>" --body-file reports/G.1.x_<short>.md || true
     `
3. After G.1.7 → run integration tests:
    `pytest -q tests/integration/test_G.1_integration.py > /reports/logs/G.1_integration.log 2>&1 || true`
4. Generate snapshot: `python scripts/generate_phase_snapshot.py`
5. Merge all branches → `prod-review/PhaseG.1-Finalization` and tag `v7.0.0-phaseG.1`.

---

## 🧮 Policy Compliance (P1–P7)

| Policy                   | Enforcement                                       |
| :----------------------- | :------------------------------------------------ |
| P1 Data Privacy          | Anonymized replication + no PII in transit        |
| P2 Secrets & Signing     | Cosign signatures for cross-region API requests   |
| P3 Execution Safety      | Approver workflow for fail-over changes           |
| P4 Observability         | Each region exposes /metrics and /global-status   |
| P5 Multi-Tenancy         | Tenant RLS across regions                         |
| P6 Performance Budget    | Latency < 500 ms intra-region, < 1 s inter-region |
| P7 Resilience & Recovery | Async snapshots + failover simulation tests       |

---

## 🧾 Required Reports

* `/reports/G.1.*.md` (one per task)
* `/reports/logs/G.1.*.log`
* `/reports/PhaseG.1_Snapshot.json`

Each report must contain:

* Branch SHA
* SIMULATION_MODE status
* Test summary
* Verification outputs
* Policy pass/block matrix
* Audit hash refs

---

## Agent Prompt (embedded)

```
You are the ATOM coding agent. Execute Phase G.1 per this document. Run compliance precheck. If any infra missing set SIMULATION_MODE=true and proceed. Implement tasks G.1.1→G.1.7, run tests, generate reports, push branches, and open PRs. Do not log secrets. Upon completion merge to prod-review/PhaseG.1-Finalization and tag v7.0.0-phaseG.1.
```

---

**End of Phase G.1 Agent File**

````

---

## **2️⃣ `/docs/compliance-precheck_G.1.md`**

```markdown
# Compliance Precheck — Phase G.1 Global Federation Readiness

**Purpose** Verify multi-region infrastructure before autonomous execution.  
**Output:** `/reports/G.1_precheck.json` + `/reports/logs/G.1_precheck.log`

---

### Checks (agent-run)

1. **Region Registry connectivity**
```bash
curl -s ${GLOBAL_REGISTRY_URL:-http://localhost:8401}/health || echo "NO_REGISTRY"
````

2. **Vault & Cosign**

```bash
python -d <<'PY'
import os,json; r={}
r["vault"]="UP" if os.getenv("VAULT_ADDR") else "MISSING"
r["cosign"]="OK" if os.getenv("COSIGN_KEY_PATH") else "MISSING"
print(json.dumps(r))
PY
```

3. **Postgres reachability**

```bash
python <<'PY'
import os,psycopg2,json
out={"postgres":{}}
dsn=os.getenv("POSTGRES_DSN")
if not dsn: out["postgres"]["status"]="MISSING"
else:
  try: psycopg2.connect(dsn,connect_timeout=3).close(); out["postgres"]["status"]="REACHABLE"
  except Exception as e: out["postgres"]["status"]=f"ERROR:{e}"
print(json.dumps(out))
PY
```

4. **Decision logic**
   Combine statuses into:

```
{
 "vault":"UP|MISSING",
 "cosign":"OK|MISSING",
 "postgres":"REACHABLE|MISSING|ERROR",
 "decision":"PROCEED|PROCEED_SIMULATION|BLOCK"
}
```

Rules:

* If all UP/OK/REACHABLE → `PROCEED`
* If some missing but registry reachable → `PROCEED_SIMULATION`
* If registry missing → `BLOCK`

Write JSON to `/reports/G.1_precheck.json`

---

```

---

