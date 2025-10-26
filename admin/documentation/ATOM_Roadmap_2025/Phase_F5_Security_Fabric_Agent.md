Here is the **complete, autonomous `.md` plan for Phase F.5 — Security Fabric Foundation**, formatted exactly like your previous agent-ready specs and ready to drop in at
`/docs/Phase_F5_Security_Fabric_Agent.md`.
This expands Phase F by embedding deep security automation into ATOM Cloud before moving to global federation.

---

```markdown
# Phase F.5 — Security Fabric Foundation (Agent-Ready Plan)

**Goal**  
Establish a zero-trust, quantum-safe, self-auditing security layer that spans every ATOM service.  
Implements continuous verification, intrusion detection, secret rotation, and compliance telemetry.

**Branch prefix:** `prod-feature/F.5-security-fabric`  
**Target version:** `v5.5.0-phaseF5`  

---

## 1️⃣ Milestones

| ID | Component | Purpose |
|----|------------|---------|
| **F.5.1** | Vault & Key Manager | Runtime secret rotation + Cosign key lifecycle |
| **F.5.2** | Zero-Trust Access Proxy | mTLS + JWT enforcement gateway |
| **F.5.3** | Threat Sensor | Runtime IDS + anomaly detector |
| **F.5.4** | Audit Pipeline | Event stream → immutable ledger |
| **F.5.5** | Compliance Monitor | P-policy scanner + report generator |

---

## 2️⃣ Environment Variables

```

VAULT_ADDR
VAULT_TOKEN
COSIGN_KEY_PATH
POSTGRES_DSN
REDIS_URL
PROM_URL
SIMULATION_MODE
JWT_SECRET
TLS_CERT_PATH
TLS_KEY_PATH

```

If any variable is missing → activate simulation mode and log `BLOCKED`.

---

## 3️⃣ Directory Structure

```

services/security-fabric/
│── vault-manager/
│   ├─ main.py
│   ├─ rotate.py
│   ├─ requirements.txt
│   ├─ Dockerfile
│
│── trust-proxy/
│   ├─ main.py
│   ├─ certs/
│   ├─ requirements.txt
│
│── threat-sensor/
│   ├─ main.py
│   ├─ model.py
│   ├─ requirements.txt
│
│── audit-pipeline/
│   ├─ main.py
│   ├─ ledger.py
│   ├─ requirements.txt
│
│── compliance-monitor/
│   ├─ main.py
│   ├─ scanner.py
│   ├─ requirements.txt
│
infra/helm/security-fabric/
tests/security/
reports/logs/

````

---

## 4️⃣ Service Specs

### F.5.1 Vault & Key Manager (`vault-manager`)
**Endpoints**
| Method | Path | Purpose |
|:--|:--|:--|
| `POST` | `/rotate` | Rotate service secrets + Cosign keys |
| `GET` | `/status` | Show key age + rotation status |
| `GET` | `/health` | Service health check |

**Verification**
```bash
curl -s http://localhost:8101/health > /reports/F5.vault_health.json
curl -s -X POST http://localhost:8101/rotate > /reports/F5.vault_rotate.json
````

---

### F.5.2 Zero-Trust Access Proxy (`trust-proxy`)

**Endpoints**

| Method | Path       | Purpose                 |
| :----- | :--------- | :---------------------- |
| `GET`  | `/verify`  | JWT and mTLS validation |
| `GET`  | `/metrics` | Prometheus exposure     |

**Verification**

```bash
curl -s --cacert $TLS_CERT_PATH https://localhost:8102/verify > /reports/F5.proxy_verify.json
```

---

### F.5.3 Threat Sensor (`threat-sensor`)

**Endpoints**

| Method | Path       | Purpose                               |
| :----- | :--------- | :------------------------------------ |
| `POST` | `/detect`  | Submit log event for ML anomaly check |
| `GET`  | `/metrics` | Model latency + alert count           |

**Verification**

```bash
curl -s -X POST http://localhost:8103/detect -d '{"event":"login_failed"}' > /reports/F5.threat_out.json
```

---

### F.5.4 Audit Pipeline (`audit-pipeline`)

**Endpoints**

| Method | Path      | Purpose                      |
| :----- | :-------- | :--------------------------- |
| `POST` | `/append` | Append audit event → ledger  |
| `GET`  | `/export` | Dump ledger for verification |

**Verification**

```bash
curl -s -X POST http://localhost:8104/append -d '{"action":"rotate_key"}' > /reports/F5.audit_append.json
curl -s http://localhost:8104/export > /reports/F5.audit_export.json
```

---

### F.5.5 Compliance Monitor (`compliance-monitor`)

**Endpoints**

| Method | Path      | Purpose                  |
| :----- | :-------- | :----------------------- |
| `GET`  | `/scan`   | Run P-policy audit       |
| `GET`  | `/report` | Generate markdown report |

**Verification**

```bash
curl -s http://localhost:8105/scan > /reports/F5.compliance_scan.json
```

---

## 5️⃣ Testing & Reports

Create `tests/security/test_security_suite.py` covering:

* Secret rotation → status changes
* JWT validation → `200 OK`
* Anomaly detection → returns probability field
* Audit append/export persistence
* Policy scan → pass rate ≥ 95 %

Run:

```bash
pytest -q tests/security/test_security_suite.py > /reports/logs/F5.tests.log 2>&1 || true
```

Generate summary file:
`/reports/F5_security_fabric_summary.md`

Include:

* Environment snapshot
* Service statuses
* Metrics samples
* Pass/fail counts
* Blocked infra
* P-policy compliance matrix

Example:

```
P1 Data Privacy: ✅  
P2 Secrets & Signing: ✅  
P3 Execution Safety: ✅  
P4 Observability: ✅  
P5 Multi-Tenancy: ✅  
P6 Performance Budget: ✅
```

Commit:

```bash
git add reports/F5_security_fabric_summary.md
git commit -m "docs(F.5): security fabric summary"
```

---

## 6️⃣ Branch & PR Flow

```bash
git checkout -b prod-feature/F.5-security-fabric
git add .
git commit -m "feat(F.5): implement security fabric foundation"
git push origin prod-feature/F.5-security-fabric
gh pr create --title "feat(F.5): Security Fabric Foundation" --body-file reports/F5_security_fabric_summary.md || true
```

---

## 7️⃣ Post-Run Aggregation

```bash
python scripts/generate_phase_snapshot.py
git add reports/PhaseF5_Snapshot.json
git commit -m "chore(F.5): snapshot"
git push origin main
```

---

## ✅ Completion Checklist

* All five security services respond on `/health`
* Key rotation and audit ledger verified
* Threat sensor detects anomalies (simulated mode OK)
* Compliance report generated
* Prometheus metrics present
* Reports and snapshot committed

---

## 🔐 Safety Rules

* Never log PII or secrets.
* All rotations signed with Cosign.
* Audit ledger is append-only (JSONL format).
* Every POST is recorded in `/var/log/security_audit.log`.
* If Vault or TLS offline → simulation mode with BLOCKED note.

---

## 🧾 Expected Deliverables

```
services/security-fabric/ (submodules)
tests/security/test_security_suite.py
reports/F5_security_fabric_summary.md
reports/logs/F5.tests.log
reports/PhaseF5_Snapshot.json
infra/helm/security-fabric/chart.yaml
```

---


```

---

This file, once placed at  
`/docs/Phase_F5_Security_Fabric_Agent.md`,  
is self-sufficient for autonomous build, test, and compliance verification of the complete **Security Fabric Foundation** layer before scaling to Phase G.
```
