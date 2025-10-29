Confirmed. Below is the **complete, agent-ready `.md` build file** for  

> **Phase G.5 — Policy Hub & Edge Mesh Relay**

It continues seamlessly from G.4, enabling distributed **policy federation, edge inference cache, and mesh synchronization**.  
Drop it into `/docs/Phase_G.5_Policy_Hub_Agent.md` — it is fully autonomous, simulation-safe, and ATOM-agent compatible.

---

```markdown
# Phase G.5 — Policy Hub & Edge Mesh Relay (Agent-Ready Build Plan)

**Goal**  
Implement the global policy synchronization hub and edge AI relay system.  
Provide real-time policy propagation, zero-trust mesh communication, edge inference caching, and cross-cluster enforcement under P1–P7 compliance.

**Version Target:** v7.4.0-phaseG.5  
**Branch Prefix:** `prod-feature/G.5.<task>`  
**Mode:** Autonomous / Simulation fallback ready  

---

## Scope & Deliverables
1. **Policy Hub Service (G.5.1)** — global policy store + signing authority  
2. **Edge Relay Service (G.5.2)** — edge node mesh relay + zero-trust communication  
3. **Inference Cache Daemon (G.5.3)** — edge-level neural inference cache  
4. **Policy Sync Controller (G.5.4)** — synchronize and reconcile hub ↔ edge policies  
5. **Edge Compliance Auditor (G.5.5)** — validate enforcement and telemetry  
6. **Policy Portal API (G.5.6)** — expose audit reports and sync status  

---

## Environment Variables
```
POLICY_HUB_URL
EDGE_NODE_ID
EDGE_MESH_TOKEN
VAULT_ADDR
COSIGN_KEY_PATH
LOCAL_REGISTRY_URL
REDIS_URL
SIMULATION_MODE
PRIMARY_REGION
PROM_URL
```
If missing → `SIMULATION_MODE=true` and mark gaps in `/reports/G.5_precheck.json`.

---

## Policies Enforced (P1–P7)
| Policy | Enforcement |
|:--|:--|
| P1 | Policy data anonymized, no PII in hub logs |
| P2 | All policies cosign-signed; unsigned = reject |
| P3 | Edge mesh joins require human/approver signoff in prod |
| P4 | /metrics, /status for every service |
| P5 | Tenant policies isolated in namespace |
| P6 | Sync latency < 2s (simulated) |
| P7 | Auto rollback if inconsistent hash states |

---

## Tasks (G.5.1 → G.5.6)

### G.5.1 — Policy Hub Service
**Files**
```
services/policy-hub/main.py
services/policy-hub/models.py
services/policy-hub/signer.py
services/policy-hub/tests/test_hub.py
reports/G.5.1_policy_hub.md
```
**Behavior**
* Central store of signed policy manifests.
* Validates signatures and issues `policy_hash` version IDs.
* Provides APIs:
  - `POST /policy/publish`
  - `GET /policy/{id}`
  - `GET /status`
* Enforces cosign verification (P2).

---

### G.5.2 — Edge Relay Service
**Files**
```
services/edge-relay/main.py
services/edge-relay/relay.py
services/edge-relay/tests/test_relay.py
reports/G.5.2_edge_relay.md
```
**Behavior**
* Connects edge nodes to hub via WebSocket or HTTP long-polling.
* Exchanges signed messages (JWT or cosign envelope).
* Provides `/health` `/relay/status` `/relay/sync`.

---

### G.5.3 — Inference Cache Daemon
**Files**
```
services/inference-cache/main.py
services/inference-cache/cache.py
services/inference-cache/tests/test_cache.py
reports/G.5.3_inference_cache.md
```
**Behavior**
* Local edge cache of recent inference results.
* Cache invalidation triggered by new policies or model updates.
* Prometheus metric: `inference_cache_hits_total`, `misses_total`.

---

### G.5.4 — Policy Sync Controller
**Files**
```
services/policy-sync/main.py
services/policy-sync/sync.py
services/policy-sync/tests/test_sync.py
reports/G.5.4_policy_sync.md
```
**Behavior**
* Continuously compares local vs hub policy hashes.
* Sync delta via secure channel.
* Audit discrepancy count and store to `/reports/policy_sync_audit.json`.

---

### G.5.5 — Edge Compliance Auditor
**Files**
```
services/edge-auditor/main.py
services/edge-auditor/audit.py
services/edge-auditor/tests/test_audit.py
reports/G.5.5_edge_auditor.md
```
**Behavior**
* Validate active policies, cryptographic hashes, and P1–P7 adherence.
* Runs on schedule or manual trigger.
* Generate `/reports/edge_audit_summary.json`.

---

### G.5.6 — Policy Portal API
**Files**
```
services/policy-portal/main.py
services/policy-portal/routes.py
services/policy-portal/tests/test_portal.py
reports/G.5.6_policy_portal.md
```
**Behavior**
* Public API to query sync status, audit results, and last hash states.
* Read-only interface for monitoring.
* Simulate in `SIMULATION_MODE` via local JSONs.

---

## Precheck
```
python - <<'PY' > /reports/G.5_precheck.json 2>&1
import os,json
r={}
for k in ["POLICY_HUB_URL","EDGE_NODE_ID","VAULT_ADDR"]:
  r[k]=("SET" if os.getenv(k) else "MISSING")
r["decision"]="PROCEED" if r["POLICY_HUB_URL"]!="MISSING" else "PROCEED_SIMULATION"
print(json.dumps(r,indent=2))
PY
```

---

## Integration Test
```
pytest -q tests/integration/test_G.5_end2end.py > /reports/logs/G.5_end2end.log 2>&1 || true
curl -s http://localhost:8700/status > /reports/G.5_health.json || true
```

---

## Expected Outputs
```
/reports/G.5.*.md
/reports/logs/G.5.*.log
/reports/G.5_precheck.json
/reports/policy_sync_audit.json
/reports/edge_audit_summary.json
/reports/PhaseG.5_Snapshot.json
```

---

## Metrics & Observability
All services expose:
* `policy_sync_latency_ms`
* `relay_connections_active`
* `inference_cache_hits_total`
* `policy_publish_total`
* `audit_failures_total`

Collect sample snapshot:
```
curl -s http://localhost:8701/metrics > /reports/G.5_metrics_sample.txt || true
```

---

## Security & Logging
* All messages signed (cosign simulation if missing).
* Never log secrets; redact values.
* Policy Hub issues PQC-signed manifests in hybrid mode.
* Edge auditor hashes all findings before reporting.

---

## Failure Handling
* If POLICY_HUB_URL missing → simulate local-only mode.
* If cosign key missing → mark P2=BLOCKED.
* If relay fails → retry in exponential backoff.
* If sync discrepancy >3 → trigger rollback simulation.

---

## Verification Criteria
✅ Policy publish works (simulated if no infra).  
✅ Edge relay connects or simulates.  
✅ Cache invalidation on update verified.  
✅ Sync controller logs consistent hash states.  
✅ Auditor reports P1–P7 compliance.  
✅ All `/health` endpoints respond 200.  

---

## Completion Rules
* All tasks run or simulate successfully.  
* Snapshot generated: `/reports/PhaseG.5_Snapshot.json`.  
* Local tag recommendation `v7.4.0-phaseG.5`.  
* Merge branches into `prod-review/PhaseG.5-Finalization`.

---

## Embedded Agent Prompt
```
You are the ATOM coding agent. Execute Phase G.5 per this file. Run precheck. If infra missing set SIMULATION_MODE=true. Implement tasks G.5.1→G.5.6. Generate reports, logs, and PhaseG.5_Snapshot.json. Do not push branches or open PRs. Upon success, recommend tag v7.4.0-phaseG.5.
```

---

## Tag Recommendation  
`v7.4.0-phaseG.5` — Policy Hub & Edge Mesh Relay Complete

---

```

---

This completes the **Federation + Self-Hosting chain (G.1 → G.5)**.  
ATOM Cloud now has:

✅ Global Federation  
✅ Cross-Cloud Replication  
✅ Self-Hosting Capability  
✅ Global Router  
✅ Edge Policy Mesh

