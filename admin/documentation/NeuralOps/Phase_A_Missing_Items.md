Phase A — Missing Items (Agent-ready)
Create `/docs/Phase_A_Missing_Items.md` and give this to your coding agent. It lists all high-leverage gaps left after Phase A and exact, ordered tasks the agent must implement. Each task includes files to create, env, verification commands, branch names, and report outputs. No code included. Paste the **Agent Prompt** block at the end into your agent.

---

# Phase A — Missing Items (summary)

**Goal:** finish high-priority production readiness for Phase A so NeuralOps can safely consume run-history and playbooks.
**Scope (prioritized):**

1. Cosign enforcement in registry
2. Vault integration for secrets (cosign keys, DB creds)
3. WPK dry-run static validator + policy hooks
4. End-to-end K8s e2e tests (kind)
5. Observability: dashboards + PrometheusRules
6. Audit logging & run provenance
7. atomctl polish (pack/sign/run)
8. RBAC & tenant isolation (Postgres RLS)
9. Backups & DR inclusion for new tables
10. Data export pipeline for NeuralOps training

---

## Pre-run (agent must run once)

```bash
mkdir -p infra/keys infra/vault infra/policies \
  infra/monitoring infra/monitoring/rules \
  tests/e2e kind-cluster scripts \
  reports/logs reports/phaseA-missing
git add . && git commit -m "chore: prepare Phase A missing-items dirs"
```

Set environment variables (agent expects these; fallback behavior must be documented in reports):

```
POSTGRES_DSN
VAULT_ADDR
VAULT_TOKEN (or use approle)
COSIGN_KEY (or Vault reference)
PROM_URL
KUBECONFIG
MILVUS_ENDPOINT
OPENAI_KEY (optional)
S3_BUCKET (for backups)
```

---

## Task 1 — Cosign enforcement in registry

**Goal:** Reject unsigned WPK uploads. Verify cosign signature and record signature metadata.

**Files to create/modify**

```
services/workflow-registry/cosign/README.md         # usage + key management (docs)
services/workflow-registry/validators/cosign.py     # verify stub (call to cosign CLI or library)
services/workflow-registry/server.py                 # enforce verification on POST /workflows
infra/keys/cosign_policy.md                         # key handling policy (doc)
reports/0A.1_cosign_enforcement.md
```

**Behavior**

* `POST /workflows` must validate uploaded WPK is cosign-signed.
* On success store `signer`, `sig_time`, `cosign_blob` in registry metadata.
* On failure return 400 with clear message.
* Provide admin bypass endpoint `POST /workflows/{id}/override` protected by admin role (audit).

**Acceptance**

* Attempt upload of unsigned WPK → 400.
* Upload of properly signed WPK → 201 and metadata contains `signer`.
* Report includes commands and test outputs.

**Verify**

```bash
# unsigned should fail
curl -v -F "file=@examples/playbooks/restart-unhealthy.wpk.yaml" http://localhost:8000/workflows

# signed (example):
cosign sign --key $COSIGN_KEY examples/playbooks/restart-unhealthy.wpk.yaml
curl -v -F "file=@examples/playbooks/restart-unhealthy.wpk.yaml" http://localhost:8000/workflows
```

**Branch / PR**

* `prod-feature/A.cosign-enforce`
* Report: `/reports/0A.1_cosign_enforcement.md`

---

## Task 2 — Vault integration for secrets

**Goal:** Move cosign keys, DB creds, S3 creds into Vault; registry/runtime fetch secrets from Vault. Do not store plaintext.

**Files to create/modify**

```
infra/vault/policies/cosign.hcl
infra/vault/policies/registry.hcl
infra/vault/roles/langgraph-role.json
infra/vault/README.md                 # how to create roles, inject secrets
services/workflow-registry/secrets.py  # Vault client usage docstring (no creds in repo)
services/runtime-agent/secrets.py      # Vault retrieval docstring
infra/helm/values/vault-values.yaml    # chart values pointers
reports/0A.2_vault_integration.md
```

**Behavior**

* Registry and runtime must read `COSIGN_KEY_REF`, `DB_DSN_REF`, `S3_CREDS_REF` from Vault at startup.
* Provide a secure bootstrap example: `vault kv put secret/atom/cosign key=@cosign.key`
* Use Vault agent or CSI driver in Helm charts (documented in README).

**Acceptance**

* Secrets stored in Vault can be retrieved by service account `langgraph-sa`.
* No plaintext secret in repo or logs.
* Report contains Vault CLI commands used and evidence.

**Verify**

```bash
vault kv put secret/atom/test key=testvalue
# from service container (example)
vault kv get -format=json secret/atom/test
```

**Branch / PR**

* `prod-feature/A.vault-integration`
* Report: `/reports/0A.2_vault_integration.md`

---

## Task 3 — WPK dry-run static validator + policy hooks

**Goal:** Implement static validator and policy engine for WPKs. Provide categorizations and dry-run simulation sandbox.

**Files to create/modify**

```
services/workflow-registry/validator/schema_rules.md    # policy rules doc
services/workflow-registry/validator/static_validator.py # checks: resources, commands, unsafe patterns
services/workflow-registry/validator/policy_engine.py     # policy evaluation & score
services/runtime-agent/sandbox_runner.md                 # how to run dry-run in sandbox (doc)
services/workflow-registry/server.py                     # POST /workflows/{id}/dry-run endpoint
tests/validator/test_static_validator.py
reports/0A.3_dryrun_policy.md
```

**Behavior**

* `POST /workflows/{id}/dry-run` runs static checks and returns `score`, `issues[]`.
* Static checks include: disallowed hostPath, CAP_SYS_ADMIN, privileged containers, clusterrole modifications, external network calls patterns.
* Policy engine classifies result: `safe`, `caution`, `unsafe` and suggests `manual` vs `auto`.
* Provide optional sandbox execution via `kind` or `pod` for dynamic dry-run; sandbox must be isolated.

**Acceptance**

* Known unsafe pattern flagged by static test.
* Dry-run endpoint returns issues and a risk score.
* Report includes sample dry-run output.

**Verify**

```bash
curl -X POST http://localhost:8000/workflows/restart-unhealthy/dry-run
# run unit tests
pytest services/workflow-registry/tests/test_validator.py -q
```

**Branch / PR**

* `prod-feature/A.dryrun-policy`
* Report: `/reports/0A.3_dryrun_policy.md`

---

## Task 4 — End-to-end K8s e2e tests (kind)

**Goal:** Provide reproducible e2e tests using kind that deploy registry + runtime + k8s adapter and run sample WPKs (scoped smoke tests).

**Files to create**

```
tests/e2e/kind/setup_kind.sh
tests/e2e/kind/deploy_minikube.sh (or Helm notes)
tests/e2e/kind/run_rag_smoke.sh
tests/e2e/README.md
reports/0A.4_kind_e2e.md
```

**Behavior**

* Create a kind cluster.
* Helm install registry + runtime (use local images).
* Run `restart-unhealthy` or `scale-on-latency` WPK end-to-end.
* Capture logs and run artifacts.

**Acceptance**

* Smoke WPK runs to completion and `workflow_runs` contains run.
* e2e script exits 0 on success.

**Verify**

```bash
bash tests/e2e/kind/setup_kind.sh
bash tests/e2e/kind/run_rag_smoke.sh
kubectl get pods -n naksha
psql "$POSTGRES_DSN" -c "select count(*) from workflow_runs;"
```

**Branch / PR**

* `prod-feature/A.kind-e2e`
* Report: `/reports/0A.4_kind_e2e.md`

---

## Task 5 — Observability: dashboards + PrometheusRules

**Goal:** Add dashboards and alerting rules for registry, runtime, insight-engine.

**Files to create**

```
infra/monitoring/grafana/dashboards/registry.json
infra/monitoring/grafana/dashboards/runtime.json
infra/monitoring/prometheus/alerts-workflow.yaml
reports/0A.5_observability.md
```

**Behavior**

* Export dashboard JSON for Grafana (basic panels: run rate, failures, latency).
* PrometheusRule with alerts: `workflow_failure_rate`, `registry_unsigned_upload_attempts`, `insight_engine_anomaly_rate`.

**Acceptance**

* Dashboards import without error.
* Prometheus shows alert rules present.

**Verify**

```bash
kubectl -n monitoring port-forward svc/prometheus 9090:9090 &
# check rules
curl -s http://localhost:9090/api/v1/rules | jq .
```

**Branch / PR**

* `prod-feature/A.observability`
* Report: `/reports/0A.5_observability.md`

---

## Task 6 — Audit logging & run provenance

**Goal:** Add immutable audit fields to `workflow_runs` and write audit logs to object storage.

**Files to create/modify**

```
infra/db/migrations/003_add_audit_fields.sql
services/workflow-registry/audit.md
services/langgraph/hooks/audit_logger.py  # doc + stub
infra/backup/objstore_policy.md
reports/0A.6_audit.md
```

**Behavior**

* Add fields: `approved_by`, `approved_at`, `cosign_sig`, `immutable_log_path`.
* On run completion, generate an immutable audit record (JSON) and upload to S3/MinIO.
* Record `immutable_log_path` in DB.

**Acceptance**

* New columns exist.
* Example audit JSON uploaded to object store and accessible (read-only).

**Verify**

```bash
psql "$POSTGRES_DSN" -c "\d workflow_runs"
aws s3 ls s3://$S3_BUCKET/path/to/audit/
```

**Branch / PR**

* `prod-feature/A.audit`
* Report: `/reports/0A.6_audit.md`

---

## Task 7 — atomctl polish (pack/sign/run)

**Goal:** Add production-ready `atomctl` operations: `pack`, `sign` (cosign), `push`, `run`.

**Files to create**

```
cli/atomctl/README.md
cli/atomctl/atomctl_spec.md  # CLI spec & example commands
cli/atomctl/ci_sign_steps.md  # CI integration notes
reports/0A.7_atomctl.md
```

**Behavior**

* Document exact `pack` format, cosign signing steps, and `push` API flow.
* Provide CI snippet for signing images / WPKs.

**Acceptance**

* `atomctl` spec validated by CI snippet (documented).
* Developer can follow README to sign and push a WPK.

**Branch / PR**

* `prod-feature/A.atomctl`
* Report: `/reports/0A.7_atomctl.md`

---

## Task 8 — RBAC & tenancy (Postgres RLS)

**Goal:** Add tenant model and RLS policy notes. Map JWT claims to tenant_id.

**Files to create/modify**

```
infra/db/migrations/004_tenant_and_rls.sql
docs/tenancy/RLS_Policy.md
services/auth/README_RLS.md
reports/0A.8_tenancy.md
```

**Behavior**

* Add `tenant_id` to `workflow_runs` and `workflows`.
* Add RLS policy examples and migration.
* Document mapping from JWT to tenant.

**Acceptance**

* RLS policy example present and tested via psql role emulate.

**Branch / PR**

* `prod-feature/A.tenancy`
* Report: `/reports/0A.8_tenancy.md`

---

## Task 9 — Backups & DR inclusion for new tables

**Goal:** Ensure `workflow_runs` and `insight_signals` included in backups and restore tests.

**Files to create**

```
infra/backup/backup_workflow_runs.sh
infra/backup/restore_workflow_runs.sh
docs/backup/backup_plan.md
reports/0A.9_backup.md
```

**Behavior**

* Add cronjob or script that includes new tables in DB dump.
* Test restore to sandbox.

**Acceptance**

* Backup file created and restore verified.

**Verify**

```bash
bash infra/backup/backup_workflow_runs.sh
bash infra/backup/restore_workflow_runs.sh /tmp/backup.sql
```

**Branch / PR**

* `prod-feature/A.backups`
* Report: `/reports/0A.9_backup.md`

---

## Task 10 — Data export pipeline for NeuralOps training

**Goal:** Export labeled run history to vector store and training dataset.

**Files to create**

```
services/etl/export_runs/README.md
services/etl/export_runs/spec.md
infra/etl/airflow_notes.md (or cron notes)
reports/0A.10_etl.md
```

**Behavior**

* Define export schedule, format, and retention.
* Provide example script that exports recent runs into a JSONL suitable for embedding and training.
* Document training labels and schema.

**Acceptance**

* Export spec and sample JSONL file present.

**Branch / PR**

* `prod-feature/A.etl`
* Report: `/reports/0A.10_etl.md`

---

## Final verification & Phase A closure

Run after all tasks:

```bash
# unit tests
pytest -q

# sample smoke checks
curl -s http://localhost:8000/workflows | jq .
curl -sX POST http://localhost:8000/workflows -F "file=@examples/playbooks/restart-unhealthy.wpk.yaml" # expects cosign enforcement behaviour

# e2e
bash tests/e2e/kind/setup_kind.sh
bash tests/e2e/kind/run_rag_smoke.sh

# DB checks
psql "$POSTGRES_DSN" -c "select count(*) from workflow_runs;"
psql "$POSTGRES_DSN" -c "select count(*) from insight_signals;"
```

Produce single summary:

* `/reports/Phase_A_missing_summary.md` with PR links, PASS/FAIL per task, and blockers.

---

