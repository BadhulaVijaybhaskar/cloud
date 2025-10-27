Saved. Below is the **complete, agent-ready policy library** file. Commit it as `/docs/policies/POLICIES.md`. The coding agent will read this file and inject the enforcement templates, tests, and verification hooks into generated services whenever a task `.md` references P1–P6.

Paste this file verbatim.

---

# /docs/policies/POLICIES.md

# ATOM Global Policy Library (P-Series)

Canonical enforcement templates, examples, tests, and verification commands for policies P1–P6.
Agents must import these rules and implement the enforcement blocks wherever a task `.md` references a policy.

> Usage: Agent reads this file. When a task spec lists any of P1–P6 the agent:
>
> 1. Inserts the enforcement code snippet into the generated endpoint or service.
> 2. Generates unit/integration tests that validate the enforcement.
> 3. Adds verification commands to the task report.
> 4. Logs compliance result under `/reports/logs/<TASK_ID>.log`.

---

## P-1 — Data Privacy

**Goal:** Prevent accidental storage or exposure of raw PII. Store only aggregates or redacted values unless explicitly approved.

### Rules (must implement)

* Do not return raw PII fields (`email`, `phone`, `ssn`, `credit_card`) from APIs unless the request includes `scope: pii:read` and an approver record.
* When persisting training data produce redacted and hashed variants for any PII.
* All data exports must be tenant-scoped and obey RLS.

### Enforcement template (Python / FastAPI)

```python
def redact_pii(record: dict) -> dict:
    for k in ['email','phone','ssn','credit_card']:
        if k in record:
            record[k] = "<REDACTED>"
    return record

@app.get("/api/data/table/{table}")
def get_table(..., include_pii: bool = False, user=Depends(current_user)):
    if include_pii:
        if not user.has_permission('pii:read'):
            raise HTTPException(403, "PII access forbidden")
        # record approver in audit log
        audit.log(user.id, "pii_access", {"table": table})
    rows = db.query(...)
    if not include_pii:
        rows = [redact_pii(r) for r in rows]
    return rows
```

### Auto-tests (generator)

* `test_p1_redaction_blocks_unauthorized`: request without `pii:read` must not return PII.
* `test_p1_export_respects_tenant`: exports contain only tenant data.

### Verification commands (agent-run)

```bash
pytest -q tests/policies/test_p1_data_privacy.py > /reports/logs/P1.log 2>&1 || true
```

---

## P-2 — Secrets & Signing

**Goal:** All secrets managed via Vault or injected via runtime. All security-critical artifacts (WPKs, models, role-changes) must be signed and auditable.

### Rules (must implement)

* No hard-coded secrets in repo.
* Use Vault for secrets. If Vault unavailable use `SIMULATION_MODE=true`.
* All WPKs, model deployment manifests, and role-change requests must be cosign-signed before acceptance into the system.
* Role or secret changes in `production` require `approved_by` and signed record stored to Vault.

### Enforcement template

```python
from vault_client import VaultClient
from cosign_client import cosign_sign

vault = VaultClient(os.getenv("VAULT_ADDR"))

def require_approval_for_production(payload: dict, user):
    if os.getenv("ENV") == "production":
        if not payload.get("approved_by"):
            raise HTTPException(403, "Approver required in production")
        signed = cosign_sign(json.dumps(payload), key_path=os.getenv("COSIGN_KEY_PATH"))
        vault.write(f"signatures/{payload['id']}", {"signed": signed, "approver": payload["approved_by"]})
```

### Auto-tests

* `test_p2_cosign_required_in_prod`
* `test_p2_vault_write_occurs`

### Verification commands

```bash
pytest -q tests/policies/test_p2_secrets_signing.py > /reports/logs/P2.log 2>&1 || true
# validate cosign file exists or simulation flag noted in report
```

---

## P-3 — Execution Safety

**Goal:** Prevent unsafe automatic execution. Default `safety.mode = manual`. Auto actions require dry-run pass and recorded approver.

### Rules

* All workflows default to `safety.mode: manual`.
* `auto` workflows must include a `dry_run` endpoint and must be `signed` and `approved_by`.
* Destructive or cluster-level operations must emit `pre_state` and `post_state` checksums (sha256) stored in audit log.

### Enforcement template

```python
@app.post("/workflows/{id}/execute")
def execute_workflow(id: str, payload: dict, user=Depends(current_user)):
    wf = registry.get(id)
    if wf.safety_mode == "manual" and not payload.get("approved"):
        raise HTTPException(403, "Manual approval required")
    if wf.safety_mode == "auto":
        # require dry run pass and signed approval
        if not wf.dry_run_passed or not wf.signed_by:
            raise HTTPException(403, "Dry-run or signature missing")
    pre_state = snapshot_system_state()
    result = runtime.execute(wf, payload)
    post_state = snapshot_system_state()
    audit.log("workflow_exec", {"id": id, "pre": sha256(pre_state), "post": sha256(post_state), "user": user.id})
    return result
```

### Auto-tests

* `test_p3_manual_block`
* `test_p3_dryrun_requirement`

### Verification commands

```bash
pytest -q tests/policies/test_p3_execution_safety.py > /reports/logs/P3.log 2>&1 || true
```

---

## P-4 — Observability

**Goal:** Every service exposes `/health` and `/metrics`. Actions must be traceable.

### Rules

* `/health` must return `status: ok`, `components: {db, vault, cosign, storage}`.
* `/metrics` must expose Prometheus metrics including `workflow_runs_total`, `role_changes_total`, `p2_signatures_total`.
* Distributed traces (OpenTelemetry) enabled where available.

### Enforcement template

```python
from prometheus_client import Counter
workflow_runs = Counter('workflow_runs_total', 'Total workflow runs')

@app.get("/health")
def health():
    return {"status":"ok", "components": {"db": True, "vault": vault.ping(), "storage": True}}

@app.get("/metrics")
def metrics():
    return generate_latest()
```

### Auto-tests

* `test_p4_health_endpoint`
* `test_p4_metrics_exposes_workflow_counter`

### Verification commands

```bash
curl -s http://localhost:PORT/health > /reports/logs/P4_health.json || true
curl -s http://localhost:PORT/metrics | head -n 50 > /reports/logs/P4_metrics.txt || true
pytest -q tests/policies/test_p4_observability.py > /reports/logs/P4.log 2>&1 || true
```

---

## P-5 — Multi-Tenancy

**Goal:** Tenant isolation via JWT claims + Postgres Row-Level Security (RLS) or equivalent.

### Rules

* Every request must include `tenant_id` in JWT claims.
* Postgres schema enabled with RLS policies that filter by `current_setting('tenant.id')` or application-level tenant middleware.
* Admin-level endpoints require `tenant_id` override permission.

### Enforcement template

```python
def tenant_middleware(request):
    token = request.headers.get("Authorization")
    claims = jwt.decode(token, os.getenv("JWT_SECRET"))
    tenant = claims.get("tenant_id")
    if not tenant:
        raise HTTPException(401, "Missing tenant context")
    request.state.tenant = tenant

# DB usage example: set session var
db.execute(f"select set_config('tenant.id','{tenant}', true)")
```

### Auto-tests

* `test_p5_requires_tenant_jwt`
* `test_p5_rls_filters_rows`

### Verification commands

```bash
pytest -q tests/policies/test_p5_multitenancy.py > /reports/logs/P5.log 2>&1 || true
```

---

## P-6 — Performance Budget

**Goal:** Ensure agent actions and APIs respect latency and resource budgets.

### Rules

* Define default SLOs per service: p95 < 1000ms unless specified.
* Long-running jobs must be asynchronous with progress endpoints.
* Resource-consuming operations must emit cost estimate in response.

### Enforcement template

```python
@app.post("/api/data/query")
def query(payload):
    start = time.time()
    if estimate_cost(payload['sql']) > COST_THRESHOLD:
        job = enqueue_async(payload)
        return {"job_id": job.id, "status": "queued"}
    res = db.run(payload['sql'])
    latency = (time.time()-start)*1000
    if latency > 1000:
        metrics.increment('slow_query_total')
    return res
```

### Auto-tests

* `test_p6_async_for_long_queries`
* `test_p6_latency_metric_recorded`

### Verification commands

```bash
pytest -q tests/policies/test_p6_performance.py > /reports/logs/P6.log 2>&1 || true
```

---

# Policy Implementation Notes for Agents

1. **Template injection:** For every endpoint that touches secrets, data exports, role changes, or workflow execution the agent must inject the relevant policy snippet. Prefer modular helper functions (e.g., `policies.p2.require_approval_for_production`) rather than duplicating code.
2. **Simulate when blocked:** When `VAULT_ADDR`, `COSIGN_KEY_PATH`, or other infra is missing, set `SIMULATION_MODE=true`. The agent must still generate the enforcement paths but switch to stubs that write to `/tmp/simulated_vault/` and mark the test as `BLOCKED` in the report.
3. **Audit logs:** All policy enforcement actions must write audit entries to `audit.log` or `audit` DB table with `{time,user,action,data_sha256,task_id}`.
4. **Tests:** Agents must generate policy unit tests under `tests/policies/` and include them in task test runs. Failures should be reported as `BLOCKED` for infra issues and `FAIL` for outright enforcement bugs.
5. **Reports:** Every task report must include a `Policies` section summarizing P1–P6 pass/fail/blocked. Example:

   ```text
   Policies:
   P1 Data Privacy: PASS
   P2 Secrets & Signing: BLOCKED (Vault unavailable)
   P3 Execution Safety: PASS
   P4 Observability: PASS
   P5 Multi-Tenancy: PASS
   P6 Performance Budget: PASS
   ```

---

# Secrets & Keys (required env vars)

* `VAULT_ADDR`
* `VAULT_TOKEN` (only for simulation fallback tests; never commit)
* `COSIGN_KEY_PATH`
* `POSTGRES_DSN`
* `JWT_SECRET`
* `SIMULATION_MODE` (true|false)

Agents must never print these to logs. If an enforcement template writes to reports, redact values.

---

# How the Agent Confirms Compliance

* Run generated tests in `tests/policies/`.
* Execute verification curl commands and collect outputs to `/reports/logs/`.
* If dependencies unavailable, generate simulated artifacts and mark the policy as `BLOCKED` not `PASS`.
* Include `audit.log` excerpts in `/reports/<TASK_ID>_summary.md`.

---

# Remediation Guidance

If a policy check fails:

1. If failure due to missing infra (Vault/Cosign/Prometheus), mark `BLOCKED` and include remediation steps (e.g., "Install Vault and set VAULT_ADDR").
2. If enforcement code failed tests, agent must open PR with failing test and fixes. PR body must include policy remediation notes.
3. For production-only blockers (approvals missing), agent must create an issue for manual approver assignment and mark task as `AWAITING_APPROVAL`.

---

# End of Policy Library

Commit `/docs/policies/POLICIES.md` to the repo. The coding agent will reference it when executing task `.md` plans and will inject enforcement, tests, and verification hooks automatically.
