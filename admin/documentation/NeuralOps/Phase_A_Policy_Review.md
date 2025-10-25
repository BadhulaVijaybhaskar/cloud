Perfect — yes ✅

Before starting **Phase B**, we must perform a **Phase A Policy Review**.
This ensures that all of ATOM’s security, governance, tenancy, and operational policies actually behave exactly as designed (Vault → Cosign → Dry-Run → RLS → Backup → Audit).

Here’s your complete **agent-ready deliverable set**:

---

# 📘 `/docs/Phase_A_Policy_Review.md`

````markdown
# Phase A Policy Review — Audit & Verification (Agent-Ready)

**Objective:** Validate all Phase A security + governance policies before Phase B begins.  
**Duration:** 2–3 days (auto + agent runs)  
**Branch:** `prod-review/PhaseA-Policy-Audit`

---

## 1️⃣ Scope of Review
Policies and mechanisms to verify:

| Category | Focus | Expected Behavior |
|:--|:--|:--|
| 1. Cosign Signature Integrity | Registry refuses unsigned WPKs | All uploads enforced & logged |
| 2. Vault Secret Broker | All secrets via Vault AppRole | No plaintext secrets in env |
| 3. WPK Safety Mode | Default = manual | Auto only with admin approval |
| 4. Policy Engine Dry-Run | Dry-run sim before live | Block unsafe ops |
| 5. Audit Logging | Immutable SHA-256 verified logs | Audit store append-only |
| 6. Tenancy & RLS | Tenant-isolated queries | Cross-tenant reads denied |
| 7. Backup & DR | Nightly backups + restore test | Successful checksum verify |
| 8. Observability Rules | Alerts for failures | All PrometheusRules active |
| 9. Audit Exports | ETL to NeuralOps training | JSONL present |
| 10. CI/CD Security | Cosign signing + policy gate | Unsigned images blocked |

---

## 2️⃣ Agent Tasks (ordered)

### Task 1 — Cosign & Vault Validation
**Goal:** Prove signature and secret integrity.

Files:  
- `services/workflow-registry/cosign_enforcer.py`  
- `services/vault_client.py`  
Reports: `/reports/Audit_Cosign_Vault.md`

Commands:
```bash
python services/workflow-registry/cosign_enforcer.py --verify examples/playbooks/*.wpk.yaml > /reports/Audit_Cosign.log
python services/vault_client.py --list-secrets --verify-policy > /reports/Audit_Vault.log
````

Pass criteria:

* Every WPK → `verified=true` in log.
* Vault AppRole auth successful (HTTP 200).

---

### Task 2 — Policy Engine Dry-Run Audit

Files: `services/workflow-registry/static_validator.py`, `policy_engine.py`
Report: `/reports/Audit_Dryrun.md`

Commands:

```bash
pytest services/workflow-registry/tests/test_dryrun_endpoint.py -q
curl -X POST http://localhost:8000/workflows/test/dry-run -F "file=@examples/playbooks/restart-unhealthy.wpk.yaml" | jq . > /reports/Audit_Dryrun.json
```

Pass: All “unsafe” ops → blocked; dry-run success true.

---

### Task 3 — RLS & Tenancy Audit

Files: `infra/sql/rls_policies.sql`, `services/auth/*`
Report: `/reports/Audit_RLS.md`

Commands:

```bash
psql "$POSTGRES_DSN" -f infra/sql/rls_policies.sql > /reports/Audit_RLS.log
python scripts/test_tenancy.py --simulate-cross-tenant > /reports/Audit_RLS.json
```

Pass: Cross-tenant query fails as expected.

---

### Task 4 — Backup & Restore Verification

Files: `infra/backup/backup_workflow_runs.sh`, `infra/scripts/restore_from_backup.sh`
Report: `/reports/Audit_Backup_DR.md`

Commands:

```bash
bash infra/backup/backup_workflow_runs.sh /tmp/phaseA_backup.sql
bash infra/scripts/restore_from_backup.sh /tmp/phaseA_backup.sql > /reports/Audit_Restore.log
sha256sum /tmp/phaseA_backup.sql > /reports/Audit_Backup_Hash.txt
```

Pass: Restore complete + hash match.

---

### Task 5 — Observability & Alert Validation

Files: `infra/monitoring/prometheus-rules.yaml`
Report: `/reports/Audit_Observability.md`

Commands:

```bash
curl -s http://localhost:9090/api/v1/rules | jq . > /reports/Audit_PromRules.json
curl -s http://localhost:9090/api/v1/alerts | jq . > /reports/Audit_ActiveAlerts.json
```

Pass: Workflow failure alert rule exists and fires when simulated.

---

### Task 6 — Audit Log Integrity & ETL Verification

Files: `infra/audit/s3_audit_logger.py`, `services/etl/export_runs/*`
Report: `/reports/Audit_Logs_ETL.md`

Commands:

```bash
python infra/audit/s3_audit_logger.py --verify sha > /reports/Audit_LogIntegrity.log
python services/etl/export_runs/export_to_jsonl.py > /reports/Audit_ETL.log
```

Pass: All logs SHA-verified; JSONL export exists.

---

### Task 7 — Consolidated Summary

Script: `scripts/aggregate_audit.py`

Outputs:

* `/reports/PhaseA_PolicyMatrix.json`
* `/reports/PhaseA_PolicyMatrix.md`
* `/reports/PhaseA_PolicyMatrix.csv`

Matrix columns: Policy | Implemented | Enforced | Evidence File | Pass/Fail | Notes.

---

## 3️⃣ Acceptance Criteria

* All policy checks → PASS or justified BLOCKED.
* Phase A policies have signed evidence in `/reports`.
* `PhaseA_PolicyMatrix.json` uploaded and referenced in main repo.
* CI pipeline includes `audit` job that runs these tests weekly.

---

## 4️⃣ Agent Prompt

```
You are the ATOM coding agent. Perform Phase A Policy Review per /docs/Phase_A_Policy_Review.md.

Steps:
1. Run each task (T1–T7) in order. 
2. Collect outputs under /reports/ as listed.
3. Summarize results into PhaseA_PolicyMatrix.md and .json.
4. Commit to branch prod-review/PhaseA-Policy-Audit and open PR.
If any policy cannot be tested (lack of Vault, Prometheus, etc.), mark BLOCKED and describe missing prereq.
Do not modify Phase B files until review completes.
```

---

## 5️⃣ Post-Review Actions

1. If any policy BLOCKED → open issue `Policy-Fix-<id>`.
2. Attach PhaseA_PolicyMatrix.md to final audit bundle.
3. After approval → tag `v1.0.0-phaseA-audit-passed` and proceed to Phase B.

---

**Deliverables Summary**
✅ /reports/Audit_* files
✅ /reports/PhaseA_PolicyMatrix.json / .md / .csv
✅ PR `prod-review/PhaseA-Policy-Audit`
✅ Audit bundle zip

---

**End of Phase A Policy Review**

```

---

# 🔧 Helper Files to add
```

scripts/aggregate_audit.py          # aggregates all /reports/Audit_*.md → matrix
infra/sql/rls_policies.sql          # actual RLS SQL if missing
scripts/test_tenancy.py             # cross-tenant check
infra/backup/backup_workflow_runs.sh
infra/scripts/restore_from_backup.sh
infra/audit/s3_audit_logger.py
services/etl/export_runs/export_to_jsonl.py

```

---

## 🪄 Next Action for You
1️⃣ Create `/docs/Phase_A_Policy_Review.md` with the content above.  
2️⃣ Add the helper file stubs (you can leave them empty for agent to implement).  
3️⃣ Commit and push.  
4️⃣ Hand it to your coding agent with the prompt section already inside the .md.  
5️⃣ Let it run overnight — it will generate the audit matrix and mark PASS/BLOCKED for each policy.  

---

Would you like me to generate the `aggregate_audit.py` stub and `PhaseA_PolicyMatrix.json` template (next step for agent output parsing)?
```
