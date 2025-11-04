Here’s your **Phase J.4 — Pre-Production Validation & Launch Operations (Agent-Ready Build Plan)** in standard `.md` format, completing the current sequence from J.1 → J.3.

---

# **Phase J.4 — Pre-Production Validation & Launch Operations (Agent-Ready Build Plan)**

**Project:** ATOM Cloud Platform
**Phase:** J.4 — Pre-Production Validation and Launch Ops Preparation
**Version target:** v1.1.0-phase-j4
**Branch prefix:** `prod-feature/j4.launch-prep`
**Mode:** Autonomous execution (`SIMULATION_MODE=true` until approval)

> **AGENT INSTRUCTION:** Perform system-wide validation of phases A → J.3 without activating UI traffic.
> **CRITICAL:** This phase is for simulation and readiness only — no public endpoints or user access.

---

## **Summary / Goal**

**Objective:** Validate entire ATOM Cloud stack for production readiness.
**Success Criteria:**

* [ ] Terraform and Helm plans apply cleanly in simulation
* [ ] Vault and governance services operational
* [ ] All agents and microservices respond to health checks
* [ ] Monitoring and alerting functional
* [ ] Runbook and on-call roster verified
* [ ] Reports archived to `reports/launch_day/`

---

## **Environment Variables (agent must read/use)**

```bash
SIMULATION_MODE=true
CLOUD_ENV=staging
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-cloud"
ENABLE_ALERTING=true
ENABLE_AUDIT_LOGS=true
POLICY_ENFORCEMENT=true
MONITORING_STACK=prometheus
HELM_AUTO_APPROVE=true
```

---

## **File / Directory Structure to Create (exact)**

```
infra/scripts/j4/
├── precheck.sh
├── run_validation.sh
└── postcheck.sh
reports/launch_day/
├── precheck.log
├── validation_summary.json
├── governance_report.json
└── postcheck.log
docs/runbooks/
└── launch_day_runbook.md
```

---

## **High-Level Tasks (J4.1 → J4.6)**

| ID   | Component             | Purpose                                   |
| ---- | --------------------- | ----------------------------------------- |
| J4.1 | Precheck Verification | Ensure infra and services reachable       |
| J4.2 | Governance Validation | Run I9 tests (P1–P20)                     |
| J4.3 | Monitoring Activation | Validate Prometheus + Grafana             |
| J4.4 | Alert Pipeline Test   | Generate test alerts → on-call channel    |
| J4.5 | Simulation Deployment | Deploy entire stack SIMULATION_MODE=true  |
| J4.6 | Post-Launch Archival  | Collect reports and tag release candidate |

---

## **Embedded Script (J4 Precheck)**

**File:** `infra/scripts/j4/precheck.sh`

```bash
#!/bin/bash
set -e
echo "[J4] Starting precheck..."
kubectl get pods -A > reports/launch_day/precheck.log
vault status >> reports/launch_day/precheck.log
terraform -chdir=infra/terraform plan -no-color | tee reports/launch_day/terraform_plan.log
echo "[J4] Precheck complete."
```

---

## **Integration Test Template (embedded)**

**File:** `tests/j4/test_fullstack_validation.py`

```python
import json, os, requests
def test_system_health():
    r = requests.get("http://localhost:8080/health")
    assert r.status_code == 200
def test_vault_unsealed():
    with open("reports/launch_day/precheck.log") as f:
        assert "Sealed: false" in f.read()
def test_governance_report_exists():
    assert os.path.exists("reports/I9_governance_test_report.json")
```

---

## **Agent Execution Steps (explicit sequence)**

1. Run `infra/scripts/j4/precheck.sh`
2. Execute `python -m pytest tests/j4/ -v`
3. Run `infra/scripts/j4/run_validation.sh` to simulate full stack
4. Generate `reports/launch_day/validation_summary.json`
5. Archive logs → `reports/launch_day/`
6. Notify Ops team that J.4 validation passed

---

## **Acceptance Criteria**

* [ ] All checks pass in simulation mode
* [ ] Vault unsealed and healthy
* [ ] Governance compliance ≥ 95%
* [ ] No critical alerts in validation run
* [ ] All reports exist and non-empty
* [ ] Repo tagged `v1.1.0-rc-backend`

---

## **Deliverables (explicit)**

* `docs/runbooks/launch_day_runbook.md`
* `reports/launch_day/*.json` (precheck, governance, validation)
* `infra/scripts/j4/*.sh` scripts
* Validation and rollback instructions updated

---

## **Security & Compliance Reminders**

* Enforce P1–P20 policies in simulation tests
* Rotate Vault tokens post-validation
* Delete temporary logs with sensitive data
* Verify audit log archival enabled

---

## **Notes for the Agent (embedded prompt)**

> You are executing Phase J.4 of ATOM Cloud.
> Focus on system-wide validation, not user interfaces.
> Operate entirely in `SIMULATION_MODE=true`.
> Generate compliance and health reports under `reports/launch_day/`.
> When complete, archive artifacts and prepare for Phase J.5 (Production cutover).

---

✅ **Phase J.4 Complete Definition:**
Execution of pre-production validation scripts and generation of health + governance reports with no critical alerts or policy violations.

---

