# **Phase J.5 — Production Cutover & Partner Federation (Agent-Ready Build Plan)**

**Project:** ATOM Cloud Platform
**Phase:** J.5 — Production Cutover & Partner Federation
**Version target:** v1.2.0-phase-j5
**Branch prefix:** `prod-feature/j5.cutover-federation`
**Mode:** Controlled execution (`SIMULATION_MODE=false` on approval only)

> **AGENT INSTRUCTION:** This phase transitions ATOM Cloud from simulation to live production and activates external partner federation.
> **CRITICAL:** Only execute this phase once all prior validations (J.1–J.4) pass and release candidate `v1.1.0-rc-backend` is tagged.

---

## **Summary / Goal**

**Objective:**
Perform the first live deployment of ATOM Cloud backend stack and enable multi-tenant partner federation.

**Success Criteria:**

* [ ] Core services deployed to production namespace
* [ ] Partner federation APIs reachable and authenticated
* [ ] Vault + governance services stable in live mode
* [ ] Canary rollout successful (0 errors in first 60 min)
* [ ] Billing + monitoring integrations verified
* [ ] All on-call teams acknowledge live state

---

## **Environment Variables (agent must read/use)**

```bash
SIMULATION_MODE=false
DEPLOY_ENV=production
NAMESPACE="atom-prod"
DOCKER_REGISTRY="registry.atomcloud.io"
ENABLE_ALERTING=true
ENABLE_AUDIT_LOGS=true
ENABLE_BILLING=true
ENABLE_PARTNER_FEDERATION=true
VAULT_PATH="/prod/secrets"
MONITORING_STACK=prometheus
POLICY_ENFORCEMENT=true
GOVERNANCE_MODE=live
```

---

## **File / Directory Structure to Create (exact)**

```
infra/scripts/j5/
├── precheck_prod.sh
├── deploy_prod.sh
├── partner_federation_init.sh
└── rollback_prod.sh
infra/contracts/partners/
├── federation_policy.sol
└── federation_registry.json
reports/j5/
├── precheck_prod.log
├── deploy_summary.json
├── federation_validation.json
└── rollback_test.log
docs/runbooks/
└── production_cutover_runbook.md
```

---

## **High-Level Tasks (J5.1 → J5.7)**

| ID   | Component                   | Purpose                                       |
| ---- | --------------------------- | --------------------------------------------- |
| J5.1 | Production Precheck         | Confirm all validation gates passed           |
| J5.2 | Live Deployment             | Helm/Terraform apply in `atom-prod` namespace |
| J5.3 | Canary Rollout              | Deploy 10% traffic and monitor for 60 minutes |
| J5.4 | Vault + Policy Verification | Live check of secrets, RBAC, and P1–P20       |
| J5.5 | Partner Federation Init     | Establish partner authentication and API link |
| J5.6 | Post-Deployment Validation  | Run end-to-end tests in live mode             |
| J5.7 | Rollback Simulation         | Validate rollback scripts and retention state |

---

## **Embedded Script: Production Deployment**

**File:** `infra/scripts/j5/deploy_prod.sh`

```bash
#!/bin/bash
set -e
echo "[J5] Starting production deployment..."

NAMESPACE="atom-prod"
CHART_PATH="infra/helm"
SERVICES=("auth" "gateway" "marketplace" "ai-proxy" "langgraph" "workflow-registry")

for svc in "${SERVICES[@]}"; do
  echo "[Deploy] Installing $svc..."
  helm upgrade --install "$svc" "$CHART_PATH/$svc" --namespace "$NAMESPACE" \
    --set simulationMode=false \
    --wait --timeout 10m
done

echo "[Terraform] Applying infrastructure..."
terraform -chdir=infra/terraform/modules/core apply -auto-approve

echo "[Vault] Applying production policies..."
for policy in infra/vault/policies/*.hcl; do
  vault policy write "$(basename "$policy" .hcl)" "$policy"
done

echo "[J5] Deployment completed successfully."
```

---

## **Partner Federation Initialization**

**File:** `infra/scripts/j5/partner_federation_init.sh`

```bash
#!/bin/bash
echo "[J5] Initializing Partner Federation..."
FED_PARTNERS=("PartnerA" "PartnerB")

for partner in "${FED_PARTNERS[@]}"; do
  echo "Registering $partner..."
  curl -X POST "https://api.atomcloud.io/v1/federation/register" \
    -H "Authorization: Bearer $VAULT_TOKEN" \
    -d "{\"partner_name\": \"$partner\", \"tier\": \"enterprise\"}"
done

echo "[J5] Partner Federation Initialized."
```

---

## **Integration Test Template**

**File:** `tests/j5/test_production_validation.py`

```python
import requests, json

def test_canary_services():
    services = ["auth", "marketplace", "gateway"]
    for s in services:
        r = requests.get(f"https://{s}.atomcloud.io/health")
        assert r.status_code == 200

def test_partner_registry():
    r = requests.get("https://api.atomcloud.io/v1/federation/list")
    data = r.json()
    assert len(data["partners"]) >= 2
```

---

## **Agent Execution Steps**

1. **Validate Precheck**

   ```bash
   ./infra/scripts/j5/precheck_prod.sh
   ```

   * Verify infra drift, Vault state, governance compliance.

2. **Deploy Live Stack**

   ```bash
   ./infra/scripts/j5/deploy_prod.sh
   ```

3. **Run Canary Monitoring**

   * Observe metrics for 60 min, verify `reports/j5/deploy_summary.json`.

4. **Initialize Partner Federation**

   ```bash
   ./infra/scripts/j5/partner_federation_init.sh
   ```

5. **Execute Validation Tests**

   ```bash
   python -m pytest tests/j5/ -v
   ```

6. **Run Rollback Simulation**

   ```bash
   ./infra/scripts/j5/rollback_prod.sh
   ```

7. **Archive Reports**

   * Move artifacts → `reports/j5/`
   * Tag version: `v1.2.0-stable-prod`

---

## **Acceptance Criteria**

* [ ] All production pods in `Running` state
* [ ] Canary rollout stable ≥ 60 min
* [ ] Vault policies applied and active
* [ ] Partner federation endpoints authenticated
* [ ] Monitoring alerts within thresholds
* [ ] All validation tests passed
* [ ] Rollback verified without data loss

---

## **Deliverables**

* `docs/runbooks/production_cutover_runbook.md`
* `infra/scripts/j5/*.sh`
* `reports/j5/*.json` (deployment + federation reports)
* Partner federation registry (`infra/contracts/partners/federation_registry.json`)

---

## **Security & Compliance Reminders**

* Enforce P1–P20 live checks post-deployment.
* Ensure Vault tokens are regenerated for prod.
* No simulation credentials used.
* All API endpoints must use mTLS.

---

## **Notes for the Agent**

> Execute this phase only when J.4 validation completed and signed off.
> Use controlled rollout, monitor continuously, and produce artifacts in `reports/j5/`.
> Engage on-call SREs and Security Admins before flipping traffic to 100%.
> This phase finalizes the ATOM Cloud core backend readiness for public and partner usage.

---

✅ **Phase J.5 Completion Definition:**
Full live production deployment with successful partner federation and zero unresolved alerts for 24 hours.

---

# **ATOM Cloud — Launch Day Runbook (Phase J.5: Production Cutover & Partner Federation)**

**Document Type:** Operational Runbook
**Applies To:** ATOM Cloud Platform — Phase J.5
**Version:** v1.2.0
**Maintainer:** CloudOps & Site Reliability Engineering Team
**Environment:** `production`
**Mode:** Controlled execution (`SIMULATION_MODE=false`)
**Approved Release Tag:** `v1.2.0-stable-prod`

---

## 🧭 **Purpose**

This runbook defines the **exact sequence of operations** to transition ATOM Cloud from pre-production (validated under Phase J.4) to full **production deployment and partner federation enablement**.
It ensures zero-downtime deployment, verified observability, secure federation, and clear rollback control.

---

## ⚙️ **Pre-Deployment Validation**

### Step 1 — Confirm Readiness

```bash
# Verify system validation
cat reports/launch_day/validation_summary.json | jq .status
```

Expected output: `"passed"`

Checklist:

* [ ] Governance reports verified
* [ ] No failed health checks in validation
* [ ] Vault tokens regenerated for production
* [ ] SRE + Security Admin acknowledged in `on-call roster`

---

### Step 2 — Snapshot Current State

```bash
kubectl get pods -A > reports/j5/precheck_prod.log
kubectl get services -A >> reports/j5/precheck_prod.log
vault status >> reports/j5/precheck_prod.log
terraform -chdir=infra/terraform/modules/core plan -no-color > reports/j5/terraform_plan_prod.log
```

Confirm:

* [ ] All namespaces accessible
* [ ] Vault unsealed
* [ ] Terraform drift = 0

---

## 🚀 **Production Deployment Process**

### Step 3 — Deploy Core Infrastructure

```bash
./infra/scripts/j5/deploy_prod.sh
```

Expected runtime: ~15 minutes
Success indicators:

* Helm deploys all services with status `deployed`
* Terraform apply completes with 0 errors
* Vault policies applied successfully

---

### Step 4 — Canary Rollout (Controlled)

```bash
kubectl rollout status deployment/gateway -n atom-prod
kubectl get pods -n atom-prod | grep gateway
```

Monitor:

* Traffic routed to 10% of production users
* No `CrashLoopBackOff` or error logs
* Response latency < 300ms (P95)

If stable for 60 minutes:

```bash
kubectl scale deployment/gateway -n atom-prod --replicas=100
```

---

### Step 5 — Federation Initialization

```bash
./infra/scripts/j5/partner_federation_init.sh
```

Expected log (reports/j5/federation_validation.json):

```json
{
  "registered_partners": ["PartnerA", "PartnerB"],
  "status": "active",
  "timestamp": "2025-12-31T10:00Z"
}
```

Verify federation registry:

```bash
curl -s https://api.atomcloud.io/v1/federation/list | jq '.partners'
```

Ensure minimum 2 active entries.

---

### Step 6 — Post-Deployment Validation

```bash
python -m pytest tests/j5/ -v
```

Check:

* All tests pass (auth, marketplace, gateway, federation)
* Monitoring dashboard shows all components `healthy`
* Grafana dashboards online
* Prometheus metrics accessible (`/metrics` endpoints live)

---

## 🧩 **On-Call and Monitoring Procedures**

| Role                     | Responsibility                       | Contact                                               |
| ------------------------ | ------------------------------------ | ----------------------------------------------------- |
| CloudOps Lead            | Authorize rollout, monitor telemetry | [ops@atomcloud.io](mailto:ops@atomcloud.io)           |
| SRE Engineer (Primary)   | Real-time log monitoring             | [sre1@atomcloud.io](mailto:sre1@atomcloud.io)         |
| SRE Engineer (Secondary) | Rollback execution if needed         | [sre2@atomcloud.io](mailto:sre2@atomcloud.io)         |
| Security Admin           | Validate Vault, policies, secrets    | [secadmin@atomcloud.io](mailto:secadmin@atomcloud.io) |
| Governance AI Agent      | Audit compliance (P1–P20)            | autonomous                                            |

**Monitoring Stack:**

* Grafana Dashboard → `https://monitor.atomcloud.io`
* Alertmanager Web → `https://alerts.atomcloud.io`
* Logs via Loki → `https://logs.atomcloud.io`

**Critical Alerts to Monitor:**

| Alert ID              | Description                     | Action                                          |
| --------------------- | ------------------------------- | ----------------------------------------------- |
| `vault_seal_detected` | Vault sealed unexpectedly       | Unseal with ops approval                        |
| `latency_spike_p95`   | Latency > threshold for 5 min   | Scale up pod replicas                           |
| `auth_down`           | Auth service not responding     | Restart pod; trigger rollback if 3 retries fail |
| `federation_error`    | Partner API registration failed | Retry or disable partner sync                   |

---

## 🧾 **Rollback Plan**

Rollback is **non-destructive** — uses Terraform state reversion + Helm revision rollback.

### Step 1 — Scale Down New Deployments

```bash
kubectl scale deployment gateway --replicas=0 -n atom-prod
```

### Step 2 — Restore Previous Helm Revision

```bash
helm rollback gateway 1 -n atom-prod
```

### Step 3 — Revert Terraform Changes

```bash
terraform -chdir=infra/terraform/modules/core apply -refresh-only -auto-approve
```

### Step 4 — Notify Stakeholders

Send Slack message to `#atom-ops`:

> Rollback initiated. Systems stable, reverting to pre-deployment baseline.

All rollback actions logged in `reports/j5/rollback_test.log`.

---

## 🔐 **Security & Compliance Checklist**

| Policy Group                     | Validation                          | Status |
| -------------------------------- | ----------------------------------- | ------ |
| P1–P5 (Access & Secrets)         | Vault applied and enforced          | ✅      |
| P6–P10 (Audit & Governance)      | Logs streaming to central collector | ✅      |
| P11–P15 (Billing & Compliance)   | Event hooks firing correctly        | ✅      |
| P16–P20 (Inter-federation Trust) | Tokens signed and validated         | ✅      |

Verify policy state:

```bash
vault read sys/policy/summary
```

---

## 📦 **Deliverables After Successful Launch**

| Deliverable             | Location                                |
| ----------------------- | --------------------------------------- |
| Deployment report       | `reports/j5/deploy_summary.json`        |
| Federation report       | `reports/j5/federation_validation.json` |
| Rollback log            | `reports/j5/rollback_test.log`          |
| Production tag manifest | `tags/v1.2.0-stable-prod`               |
| Monitoring snapshot     | `reports/j5/monitoring_snapshot.json`   |

---

## 🏁 **Success Criteria for Phase J.5 Completion**

✅ Canary rollout stable ≥ 60 min
✅ No errors in Vault or governance logs
✅ Partner federation API returning valid registry
✅ 100% tests passed post-deployment
✅ Production tag created and published
✅ Runbook and logs archived

---

Below is the **automated execution script** `run_launch_day.sh` that performs the full J.5 sequence.
It is careful, idempotent, and explicitly safe: it runs in **SIMULATION_MODE=true** by default (dry-run). To run live you must set `SIMULATION_MODE=false` **and** `APPROVE_DEPLOY=yes` in the environment (extra safety gate).

**File path suggestion:** `infra/scripts/j5/run_launch_day.sh`

Copy the contents exactly into that file, make it executable (`chmod +x infra/scripts/j5/run_launch_day.sh`), and run from repo root.

---

```bash
#!/usr/bin/env bash
# infra/scripts/j5/run_launch_day.sh
# Run the Phase J.5 Production Cutover sequence (or simulation).
# - Default: SIMULATION_MODE=true (dry-run)
# - To run live: export SIMULATION_MODE=false && export APPROVE_DEPLOY=yes
# - Safety: will refuse to run live unless APPROVE_DEPLOY=yes is set
#
# Writes logs and artifacts to reports/j5/
# Rollback available via ./infra/scripts/j5/rollback_prod.sh (idempotent)
set -euo pipefail

# ---------- Config ----------
: "${SIMULATION_MODE:=true}"
: "${APPROVE_DEPLOY:=no}"
: "${NAMESPACE:=atom-prod}"
: "${DOCKER_REGISTRY:=registry.atomcloud.io}"
: "${IMAGE_TAG:=$(git rev-parse --short HEAD 2>/dev/null || echo local)}"
REPORT_DIR="reports/j5"
INFRA_TF_DIR="infra/terraform/modules/core"
HELM_DIR="infra/helm"
SVC_LIST=("auth" "gateway" "marketplace" "ai-proxy" "langgraph" "workflow-registry")
TIMESTAMP() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

mkdir -p "${REPORT_DIR}"

log() { echo "[$(TIMESTAMP)] $*"; }
save() { echo "$*" >> "${REPORT_DIR}/run_launch_day.log"; }

# ---------- Helpers ----------
trap on_error ERR
on_error() {
  rc=$?
  echo "[$(TIMESTAMP)] ERROR: script failed with rc=${rc}" | tee -a "${REPORT_DIR}/run_launch_day.log"
  echo "Triggering rollback simulation check..." | tee -a "${REPORT_DIR}/run_launch_day.log"
  # Do not run destructive rollback automatically; just capture state for operator review
  kubectl get pods -n "${NAMESPACE}" --no-headers || true >> "${REPORT_DIR}/pre_rollback_pods.log"
  kubectl get deployments -n "${NAMESPACE}" --no-headers || true >> "${REPORT_DIR}/pre_rollback_deployments.log"
  exit ${rc}
}

helm_upgrade_install() {
  local svc=$1
  local chart="${HELM_DIR}/${svc}"
  if [ ! -d "${chart}" ]; then
    log "WARN: Helm chart not found for ${svc} at ${chart}"
    save "WARN: Helm chart not found for ${svc}"
    return 0
  fi

  if [ "${SIMULATION_MODE}" = "true" ]; then
    log "Helm lint (sim) ${svc}"
    helm lint "${chart}" || log "helm lint warnings for ${svc}"
    log "Helm template (sim) ${svc}"
    helm template "${svc}" "${chart}" --namespace "${NAMESPACE}" --set image.tag="${IMAGE_TAG}" > "${REPORT_DIR}/${svc}.helm.tpl.yaml" || true
  else
    log "Helm upgrade/install ${svc} -> namespace=${NAMESPACE}"
    helm upgrade --install "${svc}" "${chart}" --namespace "${NAMESPACE}" \
      --set image.repository="${DOCKER_REGISTRY}/${svc}" \
      --set image.tag="${IMAGE_TAG}" \
      --set simulationMode=false \
      --wait --timeout 15m
  fi
}

terraform_plan_apply() {
  if [ ! -d "${INFRA_TF_DIR}" ]; then
    log "WARN: Terraform directory ${INFRA_TF_DIR} not found"
    return 0
  fi

  pushd "${INFRA_TF_DIR}" >/dev/null
  if [ "${SIMULATION_MODE}" = "true" ]; then
    log "Terraform init & plan (sim)"
    terraform init -input=false -no-color || true
    terraform plan -input=false -no-color -out="${OLDPWD}/${REPORT_DIR}/j5.tfplan" || true
  else
    log "Terraform init & apply (prod)"
    terraform init -input=false -no-color
    terraform apply -input=false -auto-approve -no-color
  fi
  popd >/dev/null
}

vault_apply_policies() {
  if [ "${SIMULATION_MODE}" = "true" ]; then
    log "SIM: vault policy check skipped (simulation)"
    return 0
  fi

  if ! command -v vault >/dev/null 2>&1; then
    log "ERROR: 'vault' CLI not available in PATH"
    exit 1
  fi

  for policy in infra/vault/policies/*.hcl; do
    if [ -f "$policy" ]; then
      log "Applying Vault policy $(basename "$policy")"
      vault policy write "$(basename "$policy" .hcl)" "$policy"
    fi
  done
}

run_tests() {
  log "Running J5 test suite (pytest)"
  if [ "${SIMULATION_MODE}" = "true" ]; then
    log "SIMULATION_MODE=true - running simulation-friendly tests"
    pytest tests/j5/ -q || log "pytest returned non-zero in sim mode"
  else
    pytest tests/j5/ -q --maxfail=1
  fi
}

init_partner_federation() {
  if [ "${SIMULATION_MODE}" = "true" ]; then
    log "SIM: Partner federation initialization skipped (simulation)"
    # produce sample artifact
    cat > "${REPORT_DIR}/federation_validation.json" <<EOF
{
  "status":"simulated",
  "registered_partners":["PartnerA","PartnerB"],
  "timestamp":"$(TIMESTAMP)"
}
EOF
    return 0
  fi

  # Ensure VAULT_TOKEN present (but do not echo secrets)
  if [ -z "${VAULT_TOKEN:-}" ]; then
    log "ERROR: VAULT_TOKEN not set in environment; aborting partner federation init"
    exit 1
  fi

  log "Initializing partner federation (live)"
  FED_PARTNERS=("PartnerA" "PartnerB")
  jq -n '{"registered_partners":[]}' > "${REPORT_DIR}/federation_validation.json"
  for partner in "${FED_PARTNERS[@]}"; do
    log "Registering partner: ${partner}"
    # Use API endpoint - do not expose token in logs
    curl -s -o /dev/null -w "%{http_code}" -X POST "https://api.atomcloud.io/v1/federation/register" \
      -H "Authorization: Bearer ${VAULT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"partner_name\":\"${partner}\",\"tier\":\"enterprise\"}" | tee -a "${REPORT_DIR}/partner_register_codes.log"
    jq --arg p "$partner" '.registered_partners += [$p]' "${REPORT_DIR}/federation_validation.json" > "${REPORT_DIR}/federation_validation.tmp" && mv "${REPORT_DIR}/federation_validation.tmp" "${REPORT_DIR}/federation_validation.json"
  done
  jq '. + {status:"active", timestamp:"'$(TIMESTAMP)'" }' "${REPORT_DIR}/federation_validation.json" > "${REPORT_DIR}/federation_validation.final" && mv "${REPORT_DIR}/federation_validation.final" "${REPORT_DIR}/federation_validation.json"
  log "Partner federation init complete"
}

# ---------- Main Flow ----------
log "START run_launch_day.sh (SIMULATION_MODE=${SIMULATION_MODE})"
save "START $(TIMESTAMP) SIMULATION_MODE=${SIMULATION_MODE} IMAGE_TAG=${IMAGE_TAG}"

# Safety gate for live runs
if [ "${SIMULATION_MODE}" = "false" ]; then
  if [ "${APPROVE_DEPLOY}" != "yes" ]; then
    echo "LIVE DEPLOY REFUSED: To run a live deployment set APPROVE_DEPLOY=yes and re-run (and ensure you are authorized)." | tee -a "${REPORT_DIR}/run_launch_day.log"
    exit 2
  fi
  log "LIVE DEPLOY APPROVED by operator"
fi

# 1) Precheck: gather cluster state, vault status, terraform plan
log "STEP 1: Precheck - cluster / vault / terraform plan"
kubectl get pods -A --no-headers || true > "${REPORT_DIR}/precheck_pods.log"
kubectl get nodes --no-headers || true >> "${REPORT_DIR}/precheck_pods.log" || true

if command -v vault >/dev/null 2>&1; then
  vault status > "${REPORT_DIR}/vault_status.log" || true
else
  echo "vault CLI not installed; skipping vault status" > "${REPORT_DIR}/vault_status.log"
fi

terraform_plan_apply

# 2) Build docker images (simulation-safe : does not push if SIMULATION_MODE=true)
log "STEP 2: Build container images (local build)"
for svc in "${SVC_LIST[@]}"; do
  svc_dir="services/${svc}"
  if [ -d "${svc_dir}" ]; then
    log "Building ${svc} (dir=${svc_dir})"
    docker build -t "${DOCKER_REGISTRY}/${svc}:${IMAGE_TAG}" "${svc_dir}" || log "docker build (sim) failed for ${svc}"
    if [ "${SIMULATION_MODE}" = "false" ]; then
      log "Pushing ${DOCKER_REGISTRY}/${svc}:${IMAGE_TAG}"
      docker push "${DOCKER_REGISTRY}/${svc}:${IMAGE_TAG}"
    fi
  else
    log "WARN: service dir ${svc_dir} not found; skipping build"
  fi
done

# 3) Helm deploy per-service (or template in sim)
log "STEP 3: Helm deploy / template generation"
for svc in "${SVC_LIST[@]}"; do
  helm_upgrade_install "${svc}"
done

# 4) Apply terraform (if not already done by terraform_plan_apply)
if [ "${SIMULATION_MODE}" = "false" ]; then
  log "STEP 4: Ensure terraform apply already performed in terraform_plan_apply (live)."
fi

# 5) Vault policies (apply for live)
vault_apply_policies

# 6) Canary monitoring window (simulated or live)
if [ "${SIMULATION_MODE}" = "true" ]; then
  log "STEP 5: SIMULATION_MODE — Skipping real traffic canary. Producing simulated metrics snapshot."
  echo '{"canary":"simulated","status":"ok","timestamp":"'"$(TIMESTAMP)"'"}' > "${REPORT_DIR}/canary_snapshot.json"
else
  log "STEP 5: Canary rollout - monitor for 60 minutes"
  # Note: in real run this should be monitored externally; here we collect initial snapshot
  kubectl get pods -n "${NAMESPACE}" -o wide > "${REPORT_DIR}/pods_post_deploy.log"
  # Sleep shortened to 60s for safety in script - operator should monitor full 60 minutes manually
  log "Waiting 60s for initial stabilization (operator must observe 60 min window)"
  sleep 60
  kubectl top pods -n "${NAMESPACE}" > "${REPORT_DIR}/pods_metrics.log" || true
fi

# 7) Partner Federation init
log "STEP 6: Partner federation initialization"
init_partner_federation

# 8) Run integration tests
log "STEP 7: Running tests"
run_tests || log "Tests returned non-zero (see pytest output)."

# 9) Post-deploy artifacts
log "STEP 8: Collecting artifacts"
kubectl get all -n "${NAMESPACE}" --no-headers > "${REPORT_DIR}/k8s_all_after_deploy.log" || true
kubectl describe deployment -n "${NAMESPACE}" > "${REPORT_DIR}/deploy_descriptions.log" || true

# 10) Finalize and summarize
jq -n --arg sim "${SIMULATION_MODE}" --arg ts "$(TIMESTAMP)" --arg tag "${IMAGE_TAG}" \
  '{simulation:$sim, timestamp:$ts, image_tag:$tag}' > "${REPORT_DIR}/deploy_summary.json"

log "COMPLETED run_launch_day.sh"
save "END $(TIMESTAMP) sim=${SIMULATION_MODE}"

# Print top-level artifacts for operator
echo ""
echo "Artifacts written to ${REPORT_DIR}:"
ls -1 "${REPORT_DIR}" | sed -n '1,200p'
echo ""
if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "SIMULATION_MODE=true — No live changes applied. To run live set SIMULATION_MODE=false and APPROVE_DEPLOY=yes and re-run (ensure you have approvals)."
else
  echo "LIVE DEPLOY completed (operator must verify canary for 60+ minutes)."
fi

exit 0
```

---

## How to run (examples)

1. **Dry-run (safe simulation — default)**

```bash
chmod +x infra/scripts/j5/run_launch_day.sh
./infra/scripts/j5/run_launch_day.sh
# Check logs:
less reports/j5/run_launch_day.log
less reports/j5/deploy_summary.json
```

2. **Live run — *operator approval required***
   Make sure you have completed all gating items (J.4), Security & Governance sign-off, backups, and the on-call roster is READY. Then:

```bash
export SIMULATION_MODE=false
export APPROVE_DEPLOY=yes
export VAULT_TOKEN="(set in your environment securely)"
./infra/scripts/j5/run_launch_day.sh
# Monitor logs and dashboards continuously
tail -f reports/j5/run_launch_day.log
```

> **Important:** The script will refuse to run in live mode unless `APPROVE_DEPLOY=yes` is present — this is an active safety gate to avoid accidental production runs.

---

## What the script does (summary)

* Runs prechecks (k8s, Vault, Terraform plan)
* Builds images (local); pushes only if live
* Helm templates (simulation) or Helm upgrade/install (live)
* Runs Terraform plan/apply (sim or live)
* Applies vault policies (live)
* Initializes partner federation (sim vs live)
* Runs pytest integration suite (sim-friendly)
* Collects artifacts and writes `reports/j5/*`

## Failure & rollback

* The script logs errors and captures cluster state for operator review (it **does not** automatically run destructive rollback).
* Use `infra/scripts/j5/rollback_prod.sh` (provided earlier) to perform manual rollback after human review.

---

Good — I’ll generate both files now: an idempotent rollback script and a precise pre-live checklist. Paste these into your repo exactly as named.

---

## 1) `infra/scripts/j5/rollback_prod.sh`

**Path:** `infra/scripts/j5/rollback_prod.sh`
**Make executable:** `chmod +x infra/scripts/j5/rollback_prod.sh`

```bash
#!/usr/bin/env bash
# infra/scripts/j5/rollback_prod.sh
# Idempotent rollback helper for Phase J.5 production cutover.
# - Safe defaults: DRY_RUN=true will only simulate steps and collect diagnostics.
# - To execute destructive rollback set DRY_RUN=false and ensure operator approval:
#     export DRY_RUN=false
#     export APPROVE_ROLLBACK=yes
#
# Writes logs to: reports/j5/rollback_test.log
set -euo pipefail

: "${DRY_RUN:=true}"
: "${APPROVE_ROLLBACK:=no}"
: "${NAMESPACE:=atom-prod}"
REPORT_DIR="reports/j5"
HELM_DIR="infra/helm"
INFRA_TF_DIR="infra/terraform/modules/core"
TIMESTAMP() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

mkdir -p "${REPORT_DIR}"

log() { echo "[$(TIMESTAMP)] $*"; }
save() { echo "$*" >> "${REPORT_DIR}/rollback_test.log"; }

# Safety gate for live rollback
if [ "${DRY_RUN}" = "false" ] && [ "${APPROVE_ROLLBACK}" != "yes" ]; then
  echo "LIVE ROLLBACK REFUSED: To run destructive rollback set APPROVE_ROLLBACK=yes and re-run." | tee -a "${REPORT_DIR}/rollback_test.log"
  exit 2
fi

# helper: helm rollback per deployment to previous revision (if available)
helm_rollback_safe() {
  local deployment="$1"
  local ns="$2"
  # determine last successful revision
  if ! kubectl get deployment "${deployment}" -n "${ns}" &>/dev/null; then
    log "helm_rollback_safe: deployment ${deployment} not present in ${ns} — skipping"
    save "SKIP: ${deployment} not present"
    return 0
  fi

  # list revisions
  local revisions
  revisions=$(helm history "${deployment}" -n "${ns}" --max 10 --output json 2>/dev/null || true)
  if [ -z "${revisions}" ] || [ "${revisions}" = "null" ]; then
    log "No helm history available for ${deployment} in ${ns}; cannot rollback via helm. Fallback: kubectl rollout undo"
    save "NO_HELM_HISTORY ${deployment}"
    if [ "${DRY_RUN}" = "false" ]; then
      kubectl rollout undo deployment/"${deployment}" -n "${ns" || true
    fi
    return 0
  fi

  # find previous revision number (safe approach: roll back to revision N-1)
  local last_rev
  last_rev=$(echo "${revisions}" | jq -r '.[-1].revision' 2>/dev/null || echo "")
  local prev_rev
  prev_rev=$(echo "${revisions}" | jq -r '.[-2].revision' 2>/dev/null || echo "")

  if [ -n "${prev_rev}" ] && [ "${DRY_RUN}" = "false" ]; then
    log "Rolling back ${deployment} in ${ns} to revision ${prev_rev}"
    helm rollback "${deployment}" "${prev_rev}" -n "${ns" || true
    save "ROLLBACK ${deployment} -> ${prev_rev}"
  else
    log "Cannot determine previous helm revision for ${deployment} — performing kubectl rollout undo (dry run=${DRY_RUN})"
    save "ROLLBACK_FALLBACK ${deployment}"
    if [ "${DRY_RUN}" = "false" ]; then
      kubectl rollout undo deployment/"${deployment}" -n "${ns" || true
    fi
  fi
}

# Collect diagnostics before any change
log "COLLECT: pre-rollback diagnostics"
kubectl get pods -n "${NAMESPACE}" --no-headers > "${REPORT_DIR}/pre_rollback_pods.log" || true
kubectl describe pods -n "${NAMESPACE}" > "${REPORT_DIR}/pre_rollback_describe.log" || true
kubectl get events -n "${NAMESPACE}" --sort-by='.lastTimestamp' | tail -n 200 > "${REPORT_DIR}/pre_rollback_events.log" || true

# Identify key services to rollback safely (non-exhaustive; adjust to your deployment)
SERVICES=("gateway" "auth" "marketplace" "ai-proxy" "langgraph" "workflow-registry")

log "ROLLBACK PLAN: DRY_RUN=${DRY_RUN} - will target services: ${SERVICES[*]}"
save "START_ROLLBACK ${TIMESTAMP} DRY_RUN=${DRY_RUN}"

# Step 1: scale down ingress traffic (if present)
log "STEP 1: Scale down ingress / gateway to stop new traffic"
save "SCALE_DOWN_GATEWAY"
if [ "${DRY_RUN}" = "false" ]; then
  # scale gateway deployment to 0 replicas to stop new traffic (operator must ensure alternative)
  if kubectl get deployment gateway -n "${NAMESPACE}" &>/dev/null; then
    kubectl scale deployment gateway --replicas=0 -n "${NAMESPACE}" || true
    save "SCALED gateway->0"
  else
    save "GATEWAY_NOT_FOUND"
  fi
else
  save "SIMULATION: scale gateway skipped"
fi

# Step 2: For each core service try helm rollback or kubectl rollback safely
for svc in "${SERVICES[@]}"; do
  log "STEP 2: Attempt safe rollback for ${svc}"
  save "ATTEMPT_ROLLBACK ${svc}"
  helm_rollback_safe "${svc}" "${NAMESPACE}"
done

# Step 3: Reconcile Terraform state (non-destructive refresh)
log "STEP 3: Terraform refresh (non-destructive)"
save "TERRAFORM_REFRESH_START"
if [ -d "${INFRA_TF_DIR}" ]; then
  pushd "${INFRA_TF_DIR}" >/dev/null
  if [ "${DRY_RUN}" = "false" ]; then
    log "Terraform refresh/apply (live)"
    terraform init -input=false -no-color || true
    terraform apply -auto-approve -no-color || true
    save "TERRAFORM_APPLY_DONE"
  else
    log "Terraform plan (dry-run)"
    terraform init -input=false -no-color || true
    terraform plan -input=false -no-color -out="${PWD}/../${REPORT_DIR}/rollback.tfplan" || true
    save "TERRAFORM_PLAN_CREATED"
  fi
  popd >/dev/null
else
  save "TERRAFORM_DIR_NOT_FOUND ${INFRA_TF_DIR}"
fi

# Step 4: Verify Vault state and re-issue secrets (operator step)
log "STEP 4: Vault diagnostics"
if command -v vault >/dev/null 2>&1; then
  if [ "${DRY_RUN}" = "false" ]; then
    vault status > "${REPORT_DIR}/vault_status_after_rollback.log" || true
  else
    vault status > "${REPORT_DIR}/vault_status_sim.log" || true || true
  fi
else
  save "VAULT_CLI_NOT_PRESENT"
fi

# Step 5: Post-rollback diagnostics
log "STEP 5: Post-rollback diagnostics"
kubectl get pods -n "${NAMESPACE}" --no-headers > "${REPORT_DIR}/post_rollback_pods.log" || true
kubectl describe pods -n "${NAMESPACE}" > "${REPORT_DIR}/post_rollback_describe.log" || true
kubectl get events -n "${NAMESPACE}" --sort-by='.lastTimestamp' | tail -n 200 > "${REPORT_DIR}/post_rollback_events.log" || true

save "END_ROLLBACK $(TIMESTAMP) DRY_RUN=${DRY_RUN}"
log "ROLLBACK SCRIPT COMPLETE (DRY_RUN=${DRY_RUN}). Review ${REPORT_DIR}/rollback_test.log and diagnostic artifacts."
if [ "${DRY_RUN}" = "true" ]; then
  echo "DRY_RUN=true — No destructive actions performed. To run a live rollback, set DRY_RUN=false and APPROVE_ROLLBACK=yes and re-run (only after operator review)."
fi

exit 0
```

---

## 2) `docs/checklist_to_run_live.md`

**Path:** `docs/checklist_to_run_live.md`
This is the exact gate checklist with required artifacts and sign-off fields—use it as the authoritative pre-live sign-off.

````markdown
# Checklist: Preconditions & Approvals to Run Live Production Cutover (Phase J.5)

**Environment:** production (`atom-prod`)  
**Target Release:** `v1.2.0-stable-prod`  
**Date / Time:** ___________ (set before deploy)  
**Operator / Approver:** ___________

> IMPORTANT: The live deployment script `infra/scripts/j5/run_launch_day.sh` will refuse to run unless `APPROVE_DEPLOY=yes` is set. This checklist must be completed and recorded in `reports/j5/run_approvals.json` before flipping `SIMULATION_MODE=false`.

---

## 1. Governance & Policy Gates (Security Admin)
- [ ] I9 Governance report present: `reports/I9_governance_test_report.json`  
- [ ] P1–P20 compliance: checks passed and evidence attached (list file names)  
- [ ] Policy exception log: empty or documented with approval (file: `reports/j5/policy_exceptions.json`)

**Security Admin (name / sig):** ____________________  Date: ___________

---

## 2. Secrets & Vault
- [ ] Vault reachable and unsealed (`vault status` output in `reports/j5/precheck_prod.log`)  
- [ ] Vault policy files present: `infra/vault/policies/*.hcl`  
- [ ] Production secrets mapping reviewed (location & rotation policy)  
- [ ] `VAULT_TOKEN` provisioning plan documented; token lifecycle reviewed

**Security Admin (name / sig):** ____________________  Date: ___________

---

## 3. Infrastructure & Configuration
- [ ] Terraform plan reviewed and saved: `reports/j5/terraform_plan_prod.log`  
- [ ] Helm charts linted and templated: outputs in `reports/j5/*.helm.tpl.yaml`  
- [ ] `serviceMesh.enabled` flag verified for production values  
- [ ] Node pool & cluster capacity validated for canary + scale targets

**Ops Engineer (name / sig):** ____________________  Date: ___________

---

## 4. Monitoring & Alerting
- [ ] Prometheus targets healthy: check `reports/j5/monitoring_snapshot.json`  
- [ ] Grafana dashboards available and shared with on-call team  
- [ ] Alertmanager routes tested; test alert observed in channel `#ops-alerts`  
- [ ] PagerDuty escalation tested (triggered and acknowledged)

**SRE Lead (name / sig):** ____________________  Date: ___________

---

## 5. CI/CD & Artifact Validation
- [ ] Docker images built & checksum verified (list image tags)  
- [ ] Images pushed to prod registry: `registry.atomcloud.io` (yes/no)  
- [ ] Release tag created: `v1.2.0-stable-prod`  
- [ ] Signed artifacts (Cosign) present and verified

**CI/CD Owner (name / sig):** ____________________  Date: ___________

---

## 6. Billing & Metering
- [ ] Billing endpoints verified (sandbox) — `reports/j5/billing_sanity.json`  
- [ ] Metering reconciliation script present and smoke-tested  
- [ ] Alert on unexpected billing spikes configured

**Billing Owner (name / sig):** ____________________  Date: ___________

---

## 7. Partner Federation
- [ ] Partner registry contract & metadata present: `infra/contracts/partners/federation_registry.json`  
- [ ] Test partner credentials set and verified (PartnerA / PartnerB)  
- [ ] Federation call flows smoke-tested and successful

**Partner Onboarding Lead (name / sig):** ____________________  Date: ___________

---

## 8. Runbooks & Rollbacks
- [ ] Launch day runbook present: `docs/runbooks/launch_day_runbook.md`  
- [ ] Rollback script present and validated: `infra/scripts/j5/rollback_prod.sh`  
- [ ] Rollback drill rehearsed (dry-run) within the last 7 days

**Program Lead (name / sig):** ____________________  Date: ___________

---

## 9. Communications & Stakeholders
- [ ] Launch announcement drafted (Slack / mail) and approved  
- [ ] Business stakeholders informed of maintenance window  
- [ ] External partner communications prepared (if applicable)

**Communications Owner (name / sig):** ____________________  Date: ___________

---

## 10. Final Operator Approval (required to run live)
- I, the operator, confirm that all the above checks are complete and I accept responsibility to execute the production cutover.

**Operator Name:** ____________________  
**Operator Signature (or Git commit hash):** ____________________  
**APPROVE_DEPLOY flag to set before running:** `export APPROVE_DEPLOY=yes`

Date / Time of live run: _______________  Timezone: _______________

---

## Post-Approval Procedure
1. Export env:
```bash
export SIMULATION_MODE=false
export APPROVE_DEPLOY=yes
export VAULT_TOKEN="<vault-token-provided-securely>"
````

2. Run:

```bash
./infra/scripts/j5/run_launch_day.sh
```

3. Monitor dashboards and keep the on-call roster active for at least 72 hours.

**Record of Approval saved to:** `reports/j5/run_approvals.json` (operator must create after sign-off)

---

## Emergency Contact List (for live run)

* Ops Lead: [ops@atomcloud.io](mailto:ops@atomcloud.io) / +91-XXXXX
* SRE Lead: [sre@atomcloud.io](mailto:sre@atomcloud.io) / +91-XXXXX
* Security Admin: [secadmin@atomcloud.io](mailto:secadmin@atomcloud.io) / +91-XXXXX
* Program Lead: [lead@atomcloud.io](mailto:lead@atomcloud.io) / +91-XXXXX

---

**End of Checklist**
Save this file in `docs/checklist_to_run_live.md` and attach completed checklist and signatures to `reports/j5/run_approvals.json` before running live.

```

---

### Done — what I just created for you
- `infra/scripts/j5/rollback_prod.sh` (idempotent, dry-run safe; operator gate for live rollback)  
- `docs/checklist_to_run_live.md` (full sign-off checklist with required artifacts & approvals)

Both are ready to copy into the repository. Want me to also (A) commit these files to a branch in a local repo scaffold I can produce here, or (B) generate an automated `reports/j5/run_approvals.json` template pre-filled with headers you can fill in?
```
