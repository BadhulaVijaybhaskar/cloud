Here is the **Agent-Ready Build Specification** for the next phase:

---

# ⚙️ Phase K.3 — Self-Healing & Autonomous Incident Resolution

**Branch:** `prod-feature/k3.self-healing`
**Mode:** `SIMULATION_MODE=true` (default, safe testing)
**Parent Phases:** K.1 (Autonomous Runtime), K.2 (Adaptive Scaling & Predictive Ops)
**Dependencies:** `aol-controller`, `aol-policy`, `adaptive-scaler`, `predictive-ops-engine`, `governance-api`

---

## 🎯 Objective

Extend the autonomy layer to **detect, diagnose, and self-resolve incidents** without human intervention.
Use predictive signals (from K.2) and health telemetry to run controlled repair actions within defined policy boundaries.

### Goals

* Automatic service restart or reroute on detected failure.
* Root-cause isolation and correlation using telemetry.
* Integration with governance for approval of high-impact actions.
* Post-incident audit, rollback, and learning loop.

---

## 🧩 Core Components

| Component             | Path                          | Purpose                                    | Port |
| --------------------- | ----------------------------- | ------------------------------------------ | ---- |
| **incident-detector** | `services/incident-detector/` | Correlates alerts & predictive anomalies   | 8600 |
| **healing-planner**   | `services/healing-planner/`   | Chooses remediation plan & action priority | 8601 |
| **action-executor**   | `services/action-executor/`   | Executes restart/reroute/policy scripts    | 8602 |
| **knowledge-indexer** | `services/knowledge-indexer/` | Logs incident → resolution patterns        | 8603 |

---

## 🧱 Directory Structure

```
services/
  incident-detector/
  healing-planner/
  action-executor/
  knowledge-indexer/

infra/
  terraform/modules/k3_self_heal/
  helm/k3-self-heal/
  scripts/k3/
  vault/policies/k3_self_heal.hcl

tests/
  k3/
    test_detector.py
    test_planner.py
    test_executor.py
    integration/test_full_flow.py

reports/
  k3/
```

---

## ⚙️ Infrastructure

* **Terraform:** provisions 4 deployments + service accounts + ConfigMaps.
* **Helm:** chart exposes `.Values.simulationMode`, `.Values.autonomous.enabled`, `.Values.governance.enforce`.
* **Vault Policy:** extends P1–P21 with **P22 — Autonomous Remediation Safety**.
* **Service Mesh:** auto-injection for traffic reroute tests.
* **RBAC:** executor limited to namespace-scoped operations only.

---

## 🔍 Scripts

### `infra/scripts/k3/precheck.sh`

Validates:

* Health of K.1/K.2 components.
* Vault connectivity and P22 policy presence.
* Terraform & Helm manifests.
* Reports: `reports/k3/precheck_report.json`.

### `infra/scripts/k3/deploy.sh`

Simulated deployment:

* Applies Terraform/Helm in dry-run.
* Seeds sample incidents and corrective actions.
* Outputs `reports/k3/deploy_summary.json`.

### `infra/scripts/k3/verify.sh`

Runs verification:

* Executes synthetic incident scenarios (node-failure, latency spike, service crash).
* Checks if self-healing loop restored health in simulation.
* Writes `reports/k3/verification_summary.json`.

---

## 🤖 Agent Execution Flow

1. **incident-detector** ingests anomaly + alert events.
2. **healing-planner** ranks possible resolutions (restart, reroute, scale).
3. **policy-engine** enforces P22 limits.
4. **action-executor** performs action (simulation/live).
5. **knowledge-indexer** logs the incident, action, outcome, duration.
6. **governance-api** audits each remediation.

---

## 🧠 AI Models (reused + extended)

| Model                          | Source Phase | Purpose                                     |
| ------------------------------ | ------------ | ------------------------------------------- |
| LightGBM predictor             | K.2          | Forecast degradation before failure         |
| IsolationForest                | K.2          | Detect anomalies triggering healing         |
| RCA classifier (new)           | K.3          | Diagnose root cause from correlated metrics |
| Reinforcement tuner (optional) | K.3          | Adjust healing strategy rewards             |

---

## 🧾 Deliverables Summary

| File             | Path                                    | Status  |
| ---------------- | --------------------------------------- | ------- |
| Precheck script  | `infra/scripts/k3/precheck.sh`          | ✅ ready |
| Deploy script    | `infra/scripts/k3/deploy.sh`            | ✅ ready |
| Verify script    | `infra/scripts/k3/verify.sh`            | ✅ ready |
| Terraform module | `infra/terraform/modules/k3_self_heal/` | ✅ ready |
| Helm chart       | `infra/helm/k3-self-heal/`              | ✅ ready |
| Vault policy     | `infra/vault/policies/k3_self_heal.hcl` | ✅ ready |
| Test suite       | `tests/k3/`                             | ✅ ready |
| Reports dir      | `reports/k3/`                           | ✅ ready |
| CI Workflow      | `.github/workflows/k3_self_heal.yml`    | ✅ ready |

---

## 🔐 Policy & Governance

**P22 — Autonomous Remediation Safety**

| Rule                                           | Enforcement       |
| ---------------------------------------------- | ----------------- |
| Only one healing action per service per 15 min | policy-engine     |
| Mandatory post-action verification             | controller        |
| Rollback on health regression                  | executor          |
| Incident log must include reason & duration    | knowledge-indexer |

---

## 📊 Reports Generated

| Report                                 | Description                      |
| -------------------------------------- | -------------------------------- |
| `reports/k3/precheck_report.json`      | Resource & dependency validation |
| `reports/k3/deploy_summary.json`       | Dry-run deployment summary       |
| `reports/k3/incident_samples.json`     | Simulated incident data          |
| `reports/k3/action_log.json`           | Healing actions taken            |
| `reports/k3/verification_summary.json` | Post-healing evaluation          |

---

## ✅ Test Matrix

| Test                            | Description                                |
| ------------------------------- | ------------------------------------------ |
| `test_detector.py`              | Correlates multiple alerts to one incident |
| `test_planner.py`               | Plans minimal-risk remediation             |
| `test_executor.py`              | Executes simulated restart safely          |
| `integration/test_full_flow.py` | End-to-end incident → healing validation   |

Expected: **All PASS (simulation mode)**

---

## 🧮 Simulation Mode Validation

Run:

```bash
SIMULATION_MODE=true ./infra/scripts/k3/precheck.sh
SIMULATION_MODE=true ./infra/scripts/k3/deploy.sh
SIMULATION_MODE=true ./infra/scripts/k3/verify.sh
```

Expected outputs in `reports/k3/verification_summary.json` showing:

* Healing success rate ≥ 95%
* Mean recovery time ≤ 120 s
* No governance violations

---

## 📦 CI Workflow

```yaml
name: K3 Self-Healing Verify
on:
  push:
    branches: ['prod-feature/k3.*']
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: chmod +x infra/scripts/k3/*.sh
      - run: SIMULATION_MODE=true infra/scripts/k3/precheck.sh
      - run: SIMULATION_MODE=true infra/scripts/k3/deploy.sh
      - run: SIMULATION_MODE=true infra/scripts/k3/verify.sh
      - uses: actions/upload-artifact@v4
        with:
          name: k3-reports
          path: reports/k3
```

---

## ✅ Completion Criteria

* All scripts & Helm/Terraform validated in simulation.
* Healing scenarios restored simulated health within threshold.
* Governance policy P22 fully enforced.
* CI workflow runs successfully.
* Reports uploaded and auditable.

---

