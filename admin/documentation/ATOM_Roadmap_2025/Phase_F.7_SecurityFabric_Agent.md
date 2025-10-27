Below are two agent-ready `.md` files you can drop into `/docs/` and give to your autonomous coding agent.

1. `/docs/Phase_F.7_SecurityFabric_Agent.md` — full agent-ready autonomous build plan for **Phase F.7 — Security Fabric Foundation** (services, endpoints, tests, policies, execution steps, reports, branch/PR rules).

2. `/docs/compliance-precheck_F.7.md` — compliance-precheck file that the agent runs before starting Phase F.7 (Vault, Cosign, PQC libs, secrets, smoke checks). It produces a clear PASS/BLOCKED report used by the agent to decide simulation mode.

Paste both verbatim.

---

## File 1 — `/docs/Phase_F.7_SecurityFabric_Agent.md`

```markdown
# Phase F.7 — Security Fabric Foundation (Agent-Ready Build Plan)

**Phase:** F.7 — Security Fabric Foundation  
**Goal:** Build a hardened security fabric: Vault-first secrets management, cosign signing workflows, KMS/HSM hooks, identity federation, audit pipeline, PQC readiness module, and security automation endpoints.  
**Version Target:** v6.1.0-phaseF.7  
**Branch Prefix:** `prod-feature/F.7.<task>`  
**Agent:** ATOM Coding Agent / Amazon Q Autonomous Coder

---

## Overview / Intent
This phase delivers the security backbone that enforces P2 (Secrets & Signing) across ATOM Cloud and prepares the platform for PQC (Phase H). It must be policy-first, test-driven, and produce compliance artifacts.

Core deliverables:
- Vault integration service wrappers and middleware
- Cosign signing/enforcement service and webhook
- Security-fabric (authz + identity federation) API
- Audit log pipeline and immutable storage
- HSM/KMS adapter abstraction (simulated if absent)
- PQC readiness module (keygen + test handshake)
- Policy enforcement tests and report generation

All tasks must reference `/docs/policies/POLICIES.md` and inject enforcement templates.

---

## Environment variables (required)
```

VAULT_ADDR
VAULT_ROLE
VAULT_TOKEN         # only for bootstrap; do not commit
COSIGN_KEY_PATH
KMS_PROVIDER        # "aws|gcp|hsm|mock"
HSM_ENDPOINT
POSTGRES_DSN
JWT_ISSUER
SIMULATION_MODE     # true|false (agent sets as needed)
PQC_ENABLED         # true|false

```

If critical items missing the agent must run `compliance-precheck_F.7.md` and set `SIMULATION_MODE=true` if precheck blocks.

---

## Tasks (F.7.1 → F.7.7)

| ID | Task | Summary | Service |
|----|------|---------|---------|
| F.7.1 | Vault Adapter | Vault client wrapper, secrets read/write, renew, lease handling, middleware for services | `services/vault-adapter` |
| F.7.2 | Cosign Enforcer | API to verify cosign signatures for WPKs/models; sign endpoint for CI | `services/cosign-enforcer` |
| F.7.3 | Audit Pipeline | Append-only audit log writer, retention policy, immutable storage + query API | `services/audit-pipeline` |
| F.7.4 | KMS/HSM Adapter | Adapter abstraction for KMS providers, simulated HSM for local dev | `services/kms-adapter` |
| F.7.5 | Identity Federation | OIDC federation proxy, token introspection + tenant mapping | `services/identity-federation` |
| F.7.6 | PQC Readiness | PQC keygen, hybrid handshake simulation, store keys in Vault | `services/pqc-module` |
| F.7.7 | Policy Gatekeeper | Enforcement middleware that injects P2 templates into endpoints and offers dry-run | `services/policy-gatekeeper` |

Each task below contains files to create, endpoints, tests, verification commands, policy enforcement, and acceptance criteria.

---

## Task F.7.1 — Vault Adapter

**Branch:** `prod-feature/F.7.1-vault-adapter`  
**Files to create**
```

services/vault-adapter/main.py
services/vault-adapter/vault_client.py
services/vault-adapter/requirements.txt
services/vault-adapter/tests/test_vault_adapter.py
infra/helm/vault-adapter/chart.yaml
reports/F.7.1_vault_adapter.md

````

**Endpoints / Features**
- `GET /health`
- `GET /secrets/:path` -> read secret (RBAC via JWT tenant)
- `POST /secrets/:path` -> write secret (requires approver in prod)
- Lease renewal helper and token introspect

**Policy hooks**
- Use `policies.p2.require_approval_for_production` on writes.
- Do not log secret values. Audit each read/write.

**Unit tests**
- `test_vault_read_write_simulation` (simulate Vault when `SIMULATION_MODE=true`)
- `test_vault_approver_required` (production mode)

**Verification**
```bash
pytest -q services/vault-adapter/tests/test_vault_adapter.py > /reports/logs/F.7.1.log 2>&1 || true
curl -s http://localhost:8201/health > /reports/F.7.1_health.json || true
````

**Acceptance**

* Adapter reads/writes (simulated or real)
* Writes in production require `approved_by`; signed record written to Vault or simulated store
* Audit entries generated

---

## Task F.7.2 — Cosign Enforcer

**Branch:** `prod-feature/F.7.2-cosign-enforcer`
**Files**

```
services/cosign-enforcer/main.py
services/cosign-enforcer/sign.py
services/cosign-enforcer/verify.py
services/cosign-enforcer/tests/test_cosign.py
infra/helm/cosign-enforcer/chart.yaml
reports/F.7.2_cosign_enforcer.md
```

**Endpoints**

* `POST /sign` -> sign JSON payload (CI use; requires Vault key access)
* `POST /verify` -> verify signed payload (returns verified:true/false)
* `GET /keys` -> key metadata (no private key exposure)

**Policy hooks**

* Ensure cosign key is loaded via `COSIGN_KEY_PATH` from Vault or simulated store.
* On `verify`, log `p2_signatures_total` metric.

**Tests**

* `test_cosign_sign_verify_simulation`

**Verification**

```bash
pytest -q services/cosign-enforcer/tests/test_cosign.py > /reports/logs/F.7.2.log 2>&1 || true
curl -s -X POST http://localhost:8302/verify -d '{"payload":"x","signature":"s"}' > /reports/F.7.2_verify.json || true
```

**Acceptance**

* Sign and verify endpoints function
* Signing requires approver in prod
* Keys not leaked in logs

---

## Task F.7.3 — Audit Pipeline

**Branch:** `prod-feature/F.7.3-audit-pipeline`
**Files**

```
services/audit-pipeline/main.py
services/audit-pipeline/writer.py
services/audit-pipeline/tests/test_audit.py
infra/helm/audit-pipeline/chart.yaml
reports/F.7.3_audit_pipeline.md
```

**Features**

* Append-only audit log (DB table or file + WAL)
* Immutable storage mode (object store with signed manifest)
* Query API: `GET /audit?task_id=&limit=`
* Retention / export to S3/MinIO (simulated)

**Policy hooks**

* All P2/P3 actions must call audit.write(action, meta)
* Audit entries store `data_sha256` not raw payload

**Tests**

* `test_audit_write_read`
* `test_audit_immutable_flag`

**Verification**

```bash
pytest -q services/audit-pipeline/tests/test_audit.py > /reports/logs/F.7.3.log 2>&1 || true
curl -s http://localhost:8303/audit?limit=5 > /reports/F.7.3_audit.json || true
```

**Acceptance**

* Audit entries stored and readback works
* Data stored as sha256 in audit records (sensitive payloads redacted)

---

## Task F.7.4 — KMS/HSM Adapter

**Branch:** `prod-feature/F.7.4-kms-adapter`
**Files**

```
services/kms-adapter/main.py
services/kms-adapter/provider_aws.py
services/kms-adapter/provider_hsm.py
services/kms-adapter/tests/test_kms.py
infra/helm/kms-adapter/chart.yaml
reports/F.7.4_kms_adapter.md
```

**Features**

* Abstract KMS interface: `encrypt`, `decrypt`, `sign`, `verify`
* Provider plugins: `aws`, `gcp`, `hsm`, `mock`
* HSM simulation if no HSM endpoint

**Policy hooks**

* Key material never persisted plaintext
* Vault stores provider credentials and ownership metadata

**Tests**

* `test_kms_encrypt_decrypt_simulation`

**Verification**

```bash
pytest -q services/kms-adapter/tests/test_kms.py > /reports/logs/F.7.4.log 2>&1 || true
curl -s http://localhost:8304/health > /reports/F.7.4_health.json || true
```

**Acceptance**

* Adapter supports at least `mock` provider
* Production provider requires Vault-stored creds

---

## Task F.7.5 — Identity Federation

**Branch:** `prod-feature/F.7.5-identity-federation`
**Files**

```
services/identity-federation/main.py
services/identity-federation/oidc_proxy.py
services/identity-federation/tests/test_oidc.py
infra/helm/identity-federation/chart.yaml
reports/F.7.5_identity_federation.md
```

**Features**

* OIDC proxy + token introspection endpoint
* Tenant mapping: map external issuer claims -> internal tenant_id
* Endpoint: `POST /introspect` and `GET /federation/issuers`

**Policy hooks**

* JWT tokens validated, tenant claim required (P5)
* Federation registration requires vault-backed token (P2)

**Tests**

* `test_oidc_introspection_simulation`

**Verification**

```bash
pytest -q services/identity-federation/tests/test_oidc.py > /reports/logs/F.7.5.log 2>&1 || true
curl -s http://localhost:8305/introspect -d '{"token":"x"}' > /reports/F.7.5_introspect.json || true
```

**Acceptance**

* Token introspection works (simulated if necessary)
* Tenant mapping present and enforced

---

## Task F.7.6 — PQC Readiness

**Branch:** `prod-feature/F.7.6-pqc-readiness`
**Files**

```
services/pqc-module/main.py
services/pqc-module/keygen.py
services/pqc-module/tests/test_pqc.py
infra/helm/pqc-module/chart.yaml
reports/F.7.6_pqc_readiness.md
```

**Features**

* Generate PQ keypairs (CRYSTALS-Kyber/Dilithium) in simulation
* Store key metadata in Vault (private key stored in Vault or HSM)
* Hybrid handshake simulation endpoint `POST /pqc/handshake`

**Policy hooks**

* P2: store PQ keys in Vault
* P4: log PQ readiness metrics

**Tests**

* `test_pqc_keygen_simulation`
* `test_hybrid_handshake_sim`

**Verification**

```bash
pytest -q services/pqc-module/tests/test_pqc.py > /reports/logs/F.7.6.log 2>&1 || true
curl -s http://localhost:8306/pqc/mode > /reports/F.7.6_mode.json || true
```

**Acceptance**

* PQ keypair generation works in simulation
* Key metadata written to Vault (or simulated store)

---

## Task F.7.7 — Policy Gatekeeper

**Branch:** `prod-feature/F.7.7-policy-gatekeeper`
**Files**

```
services/policy-gatekeeper/main.py
services/policy-gatekeeper/middleware.py
services/policy-gatekeeper/tests/test_gatekeeper.py
infra/helm/policy-gatekeeper/chart.yaml
reports/F.7.7_policy_gatekeeper.md
```

**Features**

* Middleware that enforces P2 & P3 templates on endpoints (dry-run, approver checks)
* `POST /policy/dryrun` to simulate policy enforcement for a payload
* `GET /policy/status` to list enforcement coverage

**Policy hooks**

* Uses `/docs/policies/POLICIES.md` snippets and injects into services on generation time

**Tests**

* `test_gatekeeper_dryrun`
* `test_gatekeeper_enforce_approver`

**Verification**

```bash
pytest -q services/policy-gatekeeper/tests/test_gatekeeper.py > /reports/logs/F.7.7.log 2>&1 || true
curl -s http://localhost:8307/policy/status > /reports/F.7.7_status.json || true
```

**Acceptance**

* Middleware enforces approver requirement for production writes
* Dry-run returns simulated effect without executing

---

## Cross-Task Requirements

* All services expose `/health` and `/metrics`
* All services write audit entries via the audit pipeline
* No secrets printed to logs. Reports must redact secrets.
* Unit tests under `services/*/tests/` and aggregated integration tests under `tests/integration/`
* Reports created: `/reports/F.7.*.md` and `/reports/logs/F.7.*.log`

---

## Execution Steps (Agent-run, exact)

1. Run compliance precheck:

   ```bash
   python3 docs/compliance-precheck_F.7.md || true
   ```

   (agent must execute the precheck script content below and write `/reports/F.7_precheck.json`)

2. If precheck PASSED, continue. If BLOCKED, set `SIMULATION_MODE=true` and record blocked components.

3. For each task F.7.1 → F.7.7:

   * `git checkout -b prod-feature/F.7.<task>-<short>`
   * Create files and implement according to task spec
   * Inject P2 & P3 templates from `/docs/policies/POLICIES.md`
   * Run `pytest` for that task and save logs:

     ```bash
     pytest -q services/<service>/tests > /reports/logs/F.7.<task>.log 2>&1 || true
     ```
   * Start service locally (uvicorn) and run verification curl commands; save outputs to `/reports/`
   * Generate `/reports/F.7.<task>_<short>.md` summarizing results and P1–P6 status
   * Commit:

     ```bash
     git add .
     git commit -m "feat(F.7.<task>): <short> - implemented (agent)"
     git push origin prod-feature/F.7.<task>-<short>
     gh pr create --title "feat(F.7.<task>): <short>" --body-file reports/F.7.<task>_<short>.md || true
     ```

4. After all tasks:

   * Run integration tests:

     ```bash
     pytest -q tests/integration/test_F.7_integration.py > /reports/logs/F.7_integration.log 2>&1 || true
     ```
   * Produce `/reports/PhaseF.7_Snapshot.json` via `scripts/generate_phase_snapshot.py`
   * Merge branches into `prod-review/PhaseF.7-Finalization`, tag `v6.1.0-phaseF.7`

---

## Reporting (required content for each report)

Each `/reports/F.7.<task>_<short>.md` must include:

* Branch and commit SHA
* Environment and SIMULATION_MODE status
* Tests run and pass/fail counts
* Verification curl outputs (health, sample endpoints)
* Policy P1–P6 table with PASS/BLOCKED/FAIL
* Audit log snippet for that task (sha256-redacted)
* Blockers and next steps

---

## Acceptance Criteria (Phase-level)

* Vault adapter and cosign enforcer functional (simulated OK)
* Audit pipeline writes immutable records with sha256 references
* KMS/HSM adapter supports mock provider
* PQC keygen simulated and stored to Vault (or simulated)
* Gatekeeper enforces approvals for production-mode writes
* All P1–P6 policies covered by tests; any infra-blocked policies marked BLOCKED in reports

---

## Safety & Secrets

* Agent must never print sensitive env vars or secrets into reports/logs
* If any code attempts to log secrets agent must redact and fail test
* For production key accesses require `approved_by` and cosign signature

---

## Agent Prompt (embedded)

```
You are the ATOM coding agent. Execute Phase F.7 per this document. Run compliance precheck. If precheck blocks, set SIMULATION_MODE=true and proceed with simulated providers. Inject P2 and P3 enforcement templates into generated endpoints. Produce reports and open PRs per task. Do not expose secrets. Start with F.7.1 and proceed sequentially.
```

---

End of Phase F.7 agent file.

````

---

## File 2 — `/docs/compliance-precheck_F.7.md`

```markdown
# Compliance Precheck — Phase F.7 Security Fabric Readiness

**Purpose:** Automated preflight checks for Vault, Cosign, KMS/HSM, and PQC libraries before Phase F.7 execution. The coding agent MUST run this precheck and save `/reports/F.7_precheck.json` before starting tasks.

---

## Precheck Steps (agent must run these commands and capture outputs)

1. **Vault reachability**
```bash
python - <<'PY'
import os, json, requests
out = {"vault": {}}
va = os.getenv("VAULT_ADDR")
if not va:
  out["vault"]["status"]="MISSING"
else:
  try:
    r = requests.get(f"{va}/v1/sys/health", timeout=5)
    out["vault"]["status"]="UP" if r.ok else f"DOWN:{r.status_code}"
  except Exception as e:
    out["vault"]["status"]=f"ERROR:{str(e)}"
print(json.dumps(out))
PY
````

2. **Cosign key presence**

```bash
python - <<'PY'
import os,json
out={"cosign":{}}
kp=os.getenv("COSIGN_KEY_PATH")
if not kp:
  out["cosign"]["status"]="MISSING"
else:
  out["cosign"]["exists"]=True if os.path.exists(kp) else False
print(json.dumps(out))
PY
```

3. **KMS/HSM provider check**

```bash
python - <<'PY'
import os,json
out={"kms":{}}
prov=os.getenv("KMS_PROVIDER","mock")
out["kms"]["provider"]=prov
if prov=="hsm":
  if os.getenv("HSM_ENDPOINT"):
    out["kms"]["status"]="HSM_CONFIGURED"
  else:
    out["kms"]["status"]="HSM_MISSING"
else:
  out["kms"]["status"]="OK (mock/managed)"
print(json.dumps(out))
PY
```

4. **PQC libs availability (optional)**

```bash
python - <<'PY'
import importlib, json
out={"pqc":{}}
try:
  ky = importlib.import_module("pqc") # placeholder; real check depends on lib names
  out["pqc"]["status"]="AVAILABLE"
except Exception:
  out["pqc"]["status"]="UNAVAILABLE"
print(json.dumps(out))
PY
```

5. **Postgres connectivity (basic)**

```bash
python - <<'PY'
import os,json,psycopg2
out={"postgres":{}}
dsn=os.getenv("POSTGRES_DSN")
if not dsn:
  out["postgres"]["status"]="MISSING"
else:
  try:
    conn=psycopg2.connect(dsn, connect_timeout=5)
    conn.close()
    out["postgres"]["status"]="REACHABLE"
  except Exception as e:
    out["postgres"]["status"]=f"ERROR:{str(e)}"
print(json.dumps(out))
PY
```

6. **Final decision logic (agent-run)**
   Agent must combine checks into `/reports/F.7_precheck.json` with keys:

```
{
 "vault":"UP|MISSING|ERROR",
 "cosign":"OK|MISSING",
 "kms":"OK|HSM_MISSING",
 "pqc":"AVAILABLE|UNAVAILABLE",
 "postgres":"REACHABLE|MISSING|ERROR",
 "decision": "PROCEED|PROCEED_SIMULATION|BLOCK"
}
```

Decision rules:

* If `vault=="UP"` AND `cosign=="OK"` AND `postgres=="REACHABLE"` → `PROCEED`.
* If any of `vault`, `cosign`, `postgres` missing but KMS mock available → `PROCEED_SIMULATION` (agent sets `SIMULATION_MODE=true`).
* If critical items missing AND no simulation fallback → `BLOCK`.

Agent must write `/reports/F.7_precheck.json` and `/reports/logs/F.7_precheck.log`.

---

## Precheck Outputs (required)

* `/reports/F.7_precheck.json` (full status + decision)
* `/reports/logs/F.7_precheck.log` (stdout/stderr of scripts)
* If decision == BLOCK → create issue `infra/PhaseF.7-precheck-blockers` with description and attach precheck JSON.

---

## Example precheck JSON

```json
{
  "vault":"UP",
  "cosign":"OK",
  "kms":"OK (mock)",
  "pqc":"UNAVAILABLE",
  "postgres":"REACHABLE",
  "decision":"PROCEED"
}
```

---

## Agent instruction (embedded)

```
Run this compliance precheck immediately. If decision is PROCEED run Phase F.7 tasks normally. If PROCEED_SIMULATION set SIMULATION_MODE=true and continue. If BLOCK open GitHub Issue and halt. Save all outputs to /reports/.
```

---

End of precheck file.

```

---

If you want I can:
- generate the test stubs under `tests/policies/` and `tests/integration/` referenced above, or
- create a `create_issues.sh` that will create the blocker issue automatically if precheck BLOCKS.

Which next?
::contentReference[oaicite:0]{index=0}
```
