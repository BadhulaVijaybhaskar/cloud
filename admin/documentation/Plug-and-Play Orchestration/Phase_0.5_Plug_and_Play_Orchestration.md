Saved. Below is the final `/docs/Phase_0.5_Plug_and_Play_Orchestration.md` content ready to drop into your repo. It includes the five starter playbooks in plain language.

# Phase 0.5 — Plug-and-Play Orchestration

**Duration:** 2 – 4 weeks (solo + AI agents)
**Goal:** Make workflows portable, versioned, validated, and safely executable inside ATOM.
**Branch prefix:** `prod-feature/0.5-<task>`

---

## Context

This phase adds the *Plug-and-Play Orchestration layer* to ATOM Cloud.
It lets developers and partners package automation workflows as **Workflow Packages (WPKs)** that ATOM can validate, sign, store, and execute safely.
This is the foundation NeuralOps will later rely on for recommending and running playbooks.

---

## Manual Pre-Run Setup (Option B — run once)

```bash
mkdir -p specs \
  examples/playbooks \
  services/workflow-registry/data \
  services/runtime-agent/logs \
  services/adapters/k8s_adapter \
  cli/atomctl \
  infra/helm/workflow-registry \
  infra/helm/runtime-agent \
  tests/specs \
  reports/logs

# Commit the folders so CI/agents don't pause on mkdir.
```

---

## Deliverables (ordered tasks)

### Task 0.5.1 — WPK Spec + Example Playbook

**Goal:** Define canonical WPK schema and one example.
**Files:** `specs/wpk_schema.yaml`, `examples/playbooks/restart-unhealthy.wpk.yaml`, `tests/specs/test_wpk_schema.py`
**Notes:** Add pytest schema validation.
**Report:** `/reports/0.5.1_wpk_schema.md`

### Task 0.5.2 — Workflow Registry Service

**Goal:** FastAPI service to register, validate, sign, and list WPKs.
**Endpoints:** `POST /workflows`, `GET /workflows`, `GET /workflows/{id}`, `POST /workflows/{id}/sign`
**Storage:** `services/workflow-registry/data/`
**Security:** Enforce cosign signing for `POST /workflows` (reject unsigned). Use Vault for cosign keys.
**Report:** `/reports/0.5.2_registry_api.md`

### Task 0.5.3 — Runtime Agent (Service Sidecar)

**Goal:** Execute WPK handlers inside a cluster sandbox.
**Endpoints:** `/init`, `/validate`, `/execute`, `/rollback`, `/health`
**Metrics:** Export Prometheus metrics (`workflow_runs_total`, `workflow_success_total`, `workflow_failure_total`).
**Path:** `services/runtime-agent/`
**Report:** `/reports/0.5.3_runtime_agent.md`

### Task 0.5.4 — K8s Adapter

**Goal:** Adapter for handler type `k8s`.
**Path:** `services/adapters/k8s_adapter/adapter.py` (or language of choice)
**Capabilities:** apply manifest, scale deployment, restart pod, run job, rollback.
**Test:** Verify using `kind` or `minikube` test script.
**Report:** `/reports/0.5.4_k8s_adapter.md`

### Task 0.5.5 — atomctl CLI

**Goal:** Developer tool to pack, push, validate, run WPKs.
**Path:** `cli/atomctl/`
**Commands:** `pack`, `validate`, `push`, `run`
**Report:** `/reports/0.5.5_atomctl.md`

### Task 0.5.6 — Registry Validator + Policy Hooks

**Goal:** Dry-run and policy check engine before execution.
**File:** `services/workflow-registry/validator.py`
**Endpoint:** `POST /workflows/{id}/dry-run`
**Behavior:** Default `safety.mode = manual`. Categorize playbooks (`manual` vs `auto`) and require org-admin approval for `auto`.
**Report:** `/reports/0.5.6_validator.md`

### Task 0.5.7 — Helm Charts + Metrics

**Goal:** Deployable charts for registry + runtime agent.
**Folders:** `infra/helm/workflow-registry/`, `infra/helm/runtime-agent/`
**Verify:** `helm template` renders successfully.
**Report:** `/reports/0.5.7_helm.md`

---

## Starter Playbooks (plain language, no code)

Place these as examples in `examples/playbooks/` and register them after Phase completion.

### 1) restart-unhealthy

* **When:** Pod crash loop or container restart count rises above threshold.
* **Steps:**

  1. Gather last 200 lines of pod logs.
  2. Capture pod events and node status.
  3. Attempt graceful restart of the pod's deployment.
  4. Verify pod health for 2 minutes.
  5. If still unhealthy, escalate to human on-call with collected logs and suggested next steps.
* **Safety:** `safety.mode = manual` by default. Admins can opt-in to `auto` after dry-run checks.

### 2) scale-on-latency

* **When:** Service latency (p95) crosses configured threshold for 3 consecutive minutes.
* **Steps:**

  1. Confirm load spike via Prometheus rate and replica CPU usage.
  2. Increase deployment replicas by computed delta (e.g., +50%).
  3. Rebalance traffic if necessary (Ingress update).
  4. Monitor latency for 5 minutes. Roll back scaling if latency unaffected.
* **Safety:** Dry-run before auto-scale; require policy allowlist for auto-scaling.

### 3) backup-verify

* **When:** Nightly scheduled backup completes (post-hook).
* **Steps:**

  1. Copy latest backup manifest to staging restore environment.
  2. Attempt a read-only restore of a small subset.
  3. Run checksum/consistency checks.
  4. Report success/failure to CI channel and create incident if failed.
* **Safety:** Non-destructive; can run auto by default.

### 4) rotate-secret

* **When:** Secret TTL approaching rotation window or on-demand.
* **Steps:**

  1. Generate new credential via Vault dynamic secrets or provider API.
  2. Inject new secret to target deployment via Kubernetes secret (rotate in place).
  3. Trigger deployment rolling restart for secret refresh.
  4. Verify service functionality and revoke old secret if successful.
* **Safety:** Requires policy guard. Default `safety.mode = manual` for high-impact secrets.

### 5) requeue-job

* **When:** A scheduled job fails with transient error (timeout, resource shortage).
* **Steps:**

  1. Inspect job logs and failure reason.
  2. If transient pattern identified, increment attempt counter and requeue job with backoff.
  3. If same job fails consecutively more than X times, escalate.
* **Safety:** Low-impact; can be `auto` by default with configured retry limits.

---

## Acceptance Criteria (Phase complete)

* WPK tarballs can be packaged → cosign-signed → validated → executed through adapter.
* All workflow runs emit Prometheus metrics.
* Vault used as broker for all secrets and signing keys.
* At least 5 starter playbooks registered and executed successfully in `kind`.
* All reports `/reports/0.5.x_*.md` exist and tests pass.

---

## Safety Rules (non-negotiable)

1. **No hard-coded secrets.** All secrets via Vault.
2. **Cosign enforcement.** Reject unsigned WPK uploads.
3. **Default `safety.mode = manual`.** Auto run requires explicit admin opt-in and audit trail.
4. **Dry-run required** for any WPK marked `auto` before first live execution.
5. **Full run logging.** Log every run to `workflow_runs` table with inputs, outputs, duration, result, and approver.

---


| Task                               |
| ---------------------------------- | 
| 0.5.1 Schema + Example             |                    
| 0.5.2 Registry API                 |                     
| 0.5.3 Runtime Agent                |                     
| 0.5.4 K8s Adapter                  |                    
| 0.5.5 atomctl CLI                  |                      
| 0.5.6 Validator + Policy Hooks     |                      
| 0.5.7 Helm Charts                  |                    
| **Total:** ~14–20 days (2–4 weeks) |                        

---

## Quick verification commands

```bash
pytest -q
curl -X POST http://localhost:8000/workflows -F 'file=@examples/playbooks/restart-unhealthy.wpk.yaml'
curl http://localhost:8000/workflows
kubectl logs deploy/runtime-agent | grep "workflow_runs_total"
helm template infra/helm/workflow-registry
```

---

## Reports & Outputs to track

* `/reports/0.5.x_<task>.md` (task reports)
* `/reports/logs/<task>.log` (failures)
* `/reports/created_dirs.txt` (phase-level record)
* `/reports/registry_signatures.log` (cosign记录)
* `workflow_runs` DB table seeded for NeuralOps training

---

## Final notes

* Cosign signing and Vault broker are mandatory checks.
* Start with the five starters. Collect run outcomes to seed NeuralOps.
* Keep `safety.mode` conservative. Move to `auto` only per org policy and after dry-run success.

---


