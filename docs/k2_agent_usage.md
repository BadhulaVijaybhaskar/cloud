# K.2 Agent Usage Guide  
**Phase:** K.2 — Adaptive Scaling & Predictive Ops  
**Purpose:** Quick reference for agents, CI, and operators to execute K.2 safely and reproducibly.

---

## 🧩 Overview
The K.2 phase extends the ATOM Autonomous Layer with predictive ML scaling.  
All operations are simulation-safe by default. Agents must never execute with live autonomy unless approvals are granted.

**Core folders:**
```
services/predictive-ops-engine/
services/adaptive-scaler/
infra/scripts/k2/
reports/k2/
models/
```

---

## ⚙️ Default Agent Execution Flow

### 1. Run Precheck
Validates all resources, artifacts, and infrastructure.
```bash
make k2-precheck
```

**Output:** `reports/k2/precheck_report.json`

### 2. Run Deploy (Simulation)
Performs Terraform + Helm simulation and generates forecast/scaling samples.
```bash
make k2-deploy SIM=true
```

**Output:** `reports/k2/deploy_summary.json`, `reports/k2/forecast_samples.json`

### 3. Verify Reports
Ensures JSON reports parse correctly and meet acceptance schema.
```bash
make k2-verify
```

**Output:** `reports/k2/verification_summary.json`

---

## 🧪 Transition to Canary (Manual Gate)

When simulation passes:

1. Security Admin, Ops Lead, and Governance Owner must approve (`docs/checklist_to_run_live.md`).
2. Operator executes live precheck:
   ```bash
   SIMULATION_MODE=false ./infra/scripts/k2/precheck.sh
   ```
3. Execute live deploy only when approvals complete:
   ```bash
   SIMULATION_MODE=false APPROVE_AUTONOMY=yes ./infra/scripts/k2/deploy.sh
   ```
4. Monitor using `verify.sh` or Prometheus dashboards for 48h.

---

## 🪄 Files & Reports Overview

| File                                   | Description                                 |
| -------------------------------------- | ------------------------------------------- |
| `reports/k2/precheck_report.json`      | Artifact validation & environment readiness |
| `reports/k2/deploy_summary.json`       | Deployment simulation results               |
| `reports/k2/forecast_samples.json`     | ML forecast samples                         |
| `reports/k2/verification_summary.json` | Final verification & recommendation         |
| `models/config/training.yaml`          | ML retraining configuration                 |
| `models/training_history.json`         | Auto-logged training and version metadata   |

---

## 🧠 Key Rules for Agents

1. Always set `SIMULATION_MODE=true` unless approved for live.
2. Respect `P1–P21` policies; never override safety gates.
3. Use Makefile targets for consistency.
4. Upload all `reports/k2/*.json` artifacts as PR evidence.
5. Record retraining logs in `models/training_history.json`.

---

**Next Phase:** K.3 — Self-Healing & Autonomous Incident Resolution
Use this file for agent-to-agent handoff reference.