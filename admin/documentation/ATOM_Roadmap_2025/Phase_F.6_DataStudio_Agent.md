Perfect. Below is your **full agent-ready `.md` file** for
`/docs/Phase_F.6_DataStudio_Agent.md`.

This is an *autonomous execution plan* for the coding agent — it includes:

* all milestones & tasks (F.6.1 → F.6.9)
* dependencies & supporting files
* explicit policy enforcement (P1–P6)
* full execution & reporting instructions

You can drop this file into your repo, reference it in a GitHub Issue labeled `phase-F.6`, and Amazon Q / ATOM Coding Agent will execute all tasks sequentially.

---

# `/docs/Phase_F.6_DataStudio_Agent.md`

```markdown
# Phase F.6 — Data Studio (Autonomous Agent Build Plan)

**Phase:** F.6 — Data Studio  
**Goal:** Convert Data Studio from static UI → fully dynamic, real-time, policy-compliant service suite.  
**Version Target:** v6.0.0-phaseF.6  
**Branch Prefix:** `prod-feature/F.6.<task>`  
**Agent:** ATOM Coding Agent / Amazon Q Autonomous Coder  

---

## 🧭 Phase Overview

**Objective:**  
Deliver a Supabase-grade developer experience within ATOM Cloud Launchpad:

| Module | Purpose |
|:--|:--|
| Schema Visualizer | Introspect & visualize DB schema |
| Table Grid CRUD | Live CRUD operations |
| SQL Editor | Real-time queries + history |
| Roles & RLS UI | Manage roles + policy simulation |
| Backup/Restore | Data safety + recovery |
| Query Plan UI | Performance visualizer |
| AI Assistant | Ask ATOM AI for SQL generation |
| Migrations Manager | Versioned SQL deployment |
| Exports & Webhooks | Data export + event hooks |

---

## 🧩 Dependencies / Base Requirements

**Environment variables**

```

POSTGRES_DSN
VAULT_ADDR
COSIGN_KEY_PATH
PROM_URL
KAFKA_URL
REDIS_URL
MINIO_ENDPOINT
JWT_SECRET
SIMULATION_MODE

```

**Existing services**
- `data-api`  (Phase F.5 dependency)  
- `auth-api`  (Phase A dependency)  
- `ai-proxy` (Phase F dependency)  
- `metrics-proxy` (Phase F dependency)

**Libraries**
```

fastapi
sqlalchemy
asyncpg
prometheus-client
pydantic
aiokafka
redis
cosign
hvac
openai

```

---

## 🧠 Applicable Policies (P1–P6)

| Policy | Implementation Summary |
|:--|:--|
| **P1 Data Privacy** | All API responses must redact PII fields unless `pii:read` scope. |
| **P2 Secrets & Signing** | Role changes and migrations must be signed via Cosign and stored in Vault. |
| **P3 Execution Safety** | Destructive queries → require `dry_run` and approver record. |
| **P4 Observability** | Every service exposes `/health` and `/metrics`. |
| **P5 Multi-Tenancy** | Tenant ID from JWT → applied in RLS and queries. |
| **P6 Performance Budget** | p95 latency ≤ 1 s; long queries handled async. |

Templates come from `/docs/policies/POLICIES.md`.  
Agents must inject them in every relevant endpoint.

---

## 🧱 Task Breakdown (F.6.1 → F.6.9)

| ID | Title | Goal | Service |
|:--|:--|:--|:--|
| F.6.1 | Schema Visualizer | Expose tables/relations API + UI graph | `data-api` |
| F.6.2 | Table CRUD Grid | Add CRUD APIs + frontend grid | `data-api` |
| F.6.3 | SQL Editor Live | Execute SQL + history/cache | `data-api` |
| F.6.4 | Roles & RLS UI | Manage roles/policies + dry-run sim | `auth-api` |
| F.6.5 | Backup & Restore | Create/list/restore backups | `backup-api` |
| F.6.6 | Query Plan UI | EXPLAIN plans + visualize costs | `metrics-proxy` |
| F.6.7 | Data Studio AI | Natural language → SQL | `ai-proxy` |
| F.6.8 | Migrations Manager | Apply/Rollback SQL versions | `migrations-api` |
| F.6.9 | Exports & Webhooks | Export data + event webhooks | `export-api` |

---

## 🧮 File Structure to Create

```

services/data-api/
services/auth-api/
services/backup-api/
services/metrics-proxy/
services/ai-proxy/
services/migrations-api/
services/export-api/
ui/data-studio/
tests/integration/
reports/
infra/helm/

````

Each service includes:  
`main.py`, `requirements.txt`, `Dockerfile`, `config.yaml`, `chart.yaml`, and a `/tests/` folder.

---

## 🧰 Core Implementation Rules

1. Every endpoint → FastAPI.  
2. All POSTs → record audit log entry.  
3. `/metrics` exposes Prometheus counters.  
4. Use Cosign + Vault when available; else simulation.  
5. Attach `tenant_id` to all DB queries via JWT.  
6. Redact PII fields in responses if scope missing.  
7. Async jobs for any operation > 1 s.  

---

## 🔧 Execution Sequence (Autonomous)

### Step 1 — Initialize
```bash
mkdir -p reports/logs
export SIMULATION_MODE=true
git checkout -b prod-feature/F.6-datastudio
````

### Step 2 — Create Service Directories and Stubs

Agent creates all services + UI pages as above.
Commit: `chore(F.6): create service skeletons`

### Step 3 — Implement Tasks Sequentially

For each task F.6.1 → F.6.9:

1. Create branch `prod-feature/F.6.<task>`
2. Generate files as per spec in `docs/tasks/F/F.6.<task>.md`
3. Inject P1–P6 templates where specified
4. Run unit tests + verification commands in that task file
5. Collect results → `/reports/F.6.<task>.md`
6. Commit and push → PR using `gh pr create --body-file /reports/F.6.<task>.md`

---

### Step 4 — Integration Test Suite

Run end-to-end validation after last task:

```bash
pytest -q tests/integration/test_F.6_end2end.py > /reports/logs/F.6_end2end.log 2>&1 || true
```

Tests must cover:

* schema visualization
* CRUD + pagination
* SQL execution + async handling
* role creation & approval enforcement (P2)
* backup restore (P2 + P6)
* AI SQL generation
* exports with tenant filter (P1 + P5)

---

### Step 5 — Verification Commands

```bash
curl -s http://localhost:8001/api/data/tables > /reports/F.6_schema.json
curl -s -X POST http://localhost:8001/api/data/query -d '{"sql":"SELECT 1"}' > /reports/F.6_query.json
curl -s http://localhost:8002/api/auth/roles > /reports/F.6_roles.json
curl -s http://localhost:8003/api/backup/list > /reports/F.6_backups.json
curl -s -X POST http://localhost:8010/api/ai/sql/suggest -d '{"context":"show users"}' > /reports/F.6_ai.json
```

---

### Step 6 — Reporting and Compliance

Generate summary:

`/reports/F.6_DataStudio_Summary.md`

**Include:**

* Commit SHA and branch
* Environment summary
* Task status F.6.1 → F.6.9
* Policy P1–P6 table
* Performance metrics (p95, throughput)
* Blocked components
* Audit log snippet

Example:

```text
P1 Data Privacy: ✅
P2 Secrets & Signing: ✅
P3 Execution Safety: ✅
P4 Observability: ✅
P5 Multi-Tenancy: ✅
P6 Performance Budget: ⚠️ (1.1 s p95)
```

Commit: `docs(F.6): add Data Studio summary`

---

### Step 7 — Phase Finalization

```bash
python scripts/generate_phase_snapshot.py
git add reports/PhaseF.6_Snapshot.json
git commit -m "chore(F.6): Phase snapshot"
git push origin main
git checkout -b prod-review/PhaseF.6-Finalization
for b in prod-feature/F.6.*; do git fetch origin "$b"; git merge --no-ff origin/"$b" -m "merge $b"; done
git push origin prod-review/PhaseF.6-Finalization
git tag -a v6.0.0-phaseF.6 -m "Phase F.6 complete"
git push origin v6.0.0-phaseF.6
```

---

## 📄 Deliverables on Completion

* 9 microservices fully implemented
* UI components for Data Studio pages
* Integration tests passed
* Reports: `/reports/F.6.1_* … /reports/F.6.9_*`
* Snapshot `PhaseF.6_Snapshot.json`
* Tag `v6.0.0-phaseF.6`
* Compliance PASS for P1–P6

---

## ⚠️ Failure Handling

If Vault, Cosign, or Prometheus unavailable:

1. Run in simulation mode.
2. Log `BLOCKED (P2)` or `BLOCKED (P4)` in report.
3. Continue execution autonomously.

---



```

```

---

---
