Understood.
Below is the **Phase H.2 Enhancement Addendum**—an *agent-ready extension* to your current H.2 documentation.
It captures and codifies the four minor additions required before the Quantum–AI Hybrid stage (H.3).
Save as `/docs/Phase_H.2_Enhancement_Addendum.md`.

---

```markdown
# Phase H.2 Enhancement Addendum — Neural Fabric → Quantum Bridge

**Purpose:**  
Harden Phase H.2 Neural Fabric Scheduler for direct transition into Phase H.3 Quantum–AI Hybrid Agents.  
Implements PQC handshake bridge, runtime hooks, telemetry policy, and environment defaults.

**Branch Prefix:** `prod-feature/H.2.enhancement.<task>`  
**Mode:** `SIMULATION_MODE=true` until GPU + PQC infra available  
**Tag Recommendation:** `v8.1.1-phaseH.2-enhanced`

---

## 🔒 H.2.E1 — Vault ↔ PQC Handshake Bridge

**Goal:** connect H.1 PQC key manager (Dilithium/Kyber) with neural-fabric TLS endpoints.

**Files**
```

services/neural-fabric-scheduler/pqc_bridge.py
tests/pqc/test_handshake_bridge.py

````

**Behavior**
- Load `VAULT_PQC_KEY_PATH` and `PQC_MODE` from env.  
- Expose `/pqc/handshake` → returns `{status:"ok", algorithm, sha256}`.  
- Use `cryptography` lib or mock if unavailable.  
- Enforce P2 (PQC signing) + P3 (approval workflow for rotation).  

**Verification**
```bash
pytest -q tests/pqc/test_handshake_bridge.py > /reports/logs/H.2.E1.log 2>&1 || true
curl -s http://localhost:8600/pqc/handshake > /reports/H.2.E1_output.json || true
````

---

## ⚙️ H.2.E2 — Runtime Hooks for Framework Integration

**Goal:** prepare PyTorch, TensorFlow, ONNX runtimes for production activation.

**Files**

```
services/neural-fabric-scheduler/runtime_hooks.py
tests/runtime/test_hooks.py
```

**Behavior**

* Check installed frameworks; fallback to `mock_runtime`.
* Provide `load_model(framework,id)` → returns simulated object.
* Register hook in `main.py` before job execution.
* Metrics: `nf_runtime_loaded_total{framework}`.

**Verification**

```bash
pytest -q tests/runtime/test_hooks.py > /reports/logs/H.2.E2.log 2>&1 || true
```

---

## 🧾 H.2.E3 — Model Telemetry Policy Document

**File:** `/docs/policies/model_telemetry.md`

**Purpose:** define collection limits for inference metrics and data retention.

**Content outline**

```
# Model Telemetry Policy
Scope: Inference metrics and performance logs only.
No PII or raw input/output stored.
Retention: 7 days simulation / 30 days production.
Metrics must aggregate per tenant, never per user.
P1 Data Privacy → strict hash anonymization.
P4 Observability → Prometheus exposure only.
```

Verification → agent must check file exists before H.3.

---

## 🌐 H.2.E4 — Default Environment Safety Settings

**File:** `.env.default`

```
NEURAL_FABRIC_MODE=simulation
SIMULATION_MODE=true
PQC_MODE=hybrid
GPU_DRIVER_MOCK=true
```

**Behavior**

* Agent ensures these defaults exist and logs env hash before execution.

Verification → presence of `.env.default` logged in `/reports/H.2.E4_envcheck.log`.

---

## ✅ Verification Checklist (Agent)

| Check                | Command                                 | Expected        |
| -------------------- | --------------------------------------- | --------------- |
| PQC Bridge Up        | `curl localhost:8600/pqc/handshake`     | `{status:"ok"}` |
| Runtime Hooks Load   | `pytest -q tests/runtime/test_hooks.py` | PASS            |
| Policy File Exists   | `ls docs/policies/model_telemetry.md`   | OK              |
| Env Defaults Present | `grep NEURAL_FABRIC_MODE .env.default`  | simulation      |

---

## 🧮 Policy Impact

| Policy                | Enhancement Effect                  |
| --------------------- | ----------------------------------- |
| P1 Data Privacy       | Telemetry policy limits data scope  |
| P2 Secrets & Signing  | Vault↔PQC bridge signs sessions     |
| P3 Execution Safety   | Key rotation approval workflow      |
| P4 Observability      | Framework metrics exposed           |
| P6 Performance Budget | Runtime hooks validated < 800 ms    |
| P7 Resilience         | Fallback to mock runtime if failure |

---

## 📦 Deliverables

* `pqc_bridge.py` module with unit test
* `runtime_hooks.py` module with unit test
* `docs/policies/model_telemetry.md`
* `.env.default` with safe defaults
* Reports `/reports/H.2.E*.md` and logs

---

## Tag Recommendation

`v8.1.1-phaseH.2-enhanced`

---

**End of H.2 Enhancement Addendum**

```

---

✅ When executed, this ensures the Neural Fabric is quantum-ready, telemetry-compliant, and framework-safe—perfectly positioned for Phase H.3 (Quantum–AI Hybrid Agents).  
Would you like me to now generate the **agent-ready .md for Phase H.3**?
```
