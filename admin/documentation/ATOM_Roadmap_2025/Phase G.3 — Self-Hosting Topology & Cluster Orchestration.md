Confirmed.
Here is the **complete, compressed, agent-ready `.md` build specification** for

> **Phase G.3 — Self-Hosting Topology & Cluster Orchestration**

The file contains every instruction, dependency, pre-check, and verification block required for your ATOM agent to execute autonomously in simulation mode or production mode.

---

```markdown
# Phase G.3 — Self-Hosting Topology & Cluster Orchestration (Agent-Ready)

**Goal**  
Enable enterprises and developers to deploy ATOM Cloud on self-hosted infrastructure (Kubernetes, Ansible, Docker, local Vault mirror, and private registry).  
Implements Helm-based orchestration, tenant-aware cluster bootstrap, and secure Vault synchronization.

**Version Target:** v7.2.0-phaseG.3  
**Branch Prefix:** `prod-feature/G.3.<task>`  
**Mode:** Autonomous / Simulation Fallback Ready  

---

## Phase Scope & Deliverables
1. **Cluster Bootstrap Service** (G.3.1) – provisions local ATOM clusters (K8s/Ansible)
2. **Registry Mirror Manager** (G.3.2) – syncs OCI images to local registry
3. **Vault Sync Daemon** (G.3.3) – replicates secrets/policies across regions
4. **Helm Orchestrator** (G.3.4) – renders Helm charts for each service
5. **Node Join Gateway** (G.3.5) – adds worker nodes securely
6. **Self-Host Policy Monitor** (G.3.6) – enforces P1–P7 compliance per cluster

---

## Environment Variables
```

K8S_CONTEXT
ANSIBLE_INVENTORY
LOCAL_REGISTRY_URL
VAULT_PRIMARY_ADDR
VAULT_SECONDARY_ADDR
COSIGN_KEY_PATH
SIMULATION_MODE
SELFHOST_REGION
ATOM_VERSION

```
If any critical variable missing → `SIMULATION_MODE=true`.

---

## Policies Enforced (P1–P7)
| Policy | Self-Host Enforcement |
|:--|:--|
| P1 | Tenant data isolated per namespace |
| P2 | Charts and secrets cosign-signed |
| P3 | Playbooks dry-run by default |
| P4 | /metrics export for each daemon |
| P5 | One namespace per tenant |
| P6 | Provision < 2 min simulation budget |
| P7 | Auto rollback on failure |

---

## Tasks (G.3.1 → G.3.6)

### G.3.1 — Cluster Bootstrap Service
**Files**
```

services/cluster-bootstrap/main.py
services/cluster-bootstrap/playbooks/bootstrap.yaml
reports/G.3.1_cluster_bootstrap.md

```
**Behavior**
* Detect K8s context or Ansible inventory  
* If missing → simulate nodes  
* Output `cluster_topology.json` with master/worker layout

**Verify**
```

pytest -q services/cluster-bootstrap/tests > /reports/logs/G.3.1.log 2>&1 || true
python services/cluster-bootstrap/main.py --simulate > /reports/G.3.1_output.json || true

```

---

### G.3.2 — Registry Mirror Manager
**Files**
```

services/registry-mirror/main.py
services/registry-mirror/sync.py
reports/G.3.2_registry_mirror.md

```
**Behavior**
* Pull ATOM images from source registry and push to `LOCAL_REGISTRY_URL`
* Cosign-sign manifests (P2)
* Track image digests in `mirror_state.json`

---

### G.3.3 — Vault Sync Daemon
**Files**
```

services/vault-sync/main.py
services/vault-sync/replicate.py
reports/G.3.3_vault_sync.md

```
**Behavior**
* Mirror secrets between `VAULT_PRIMARY_ADDR` and `VAULT_SECONDARY_ADDR`
* Verify signatures and hashes
* Maintain `vault_sync.log` for audit

---

### G.3.4 — Helm Orchestrator
**Files**
```

services/helm-orchestrator/main.py
infra/helm/atom-chart/Chart.yaml
reports/G.3.4_helm_orchestrator.md

```
**Behavior**
* Render Helm values per tenant/region
* Validate schema and signature
* In simulation mode → generate YAML without deploy

---

### G.3.5 — Node Join Gateway
**Files**
```

services/node-join/main.py
reports/G.3.5_node_join.md

```
**Behavior**
* Secure node registration with token + cosign signature
* In simulation → mock 2 nodes join sequence

---

### G.3.6 — Self-Host Policy Monitor
**Files**
```

services/selfhost-policy-monitor/main.py
docs/policies/selfhost_compliance.md
reports/G.3.6_policy_monitor.md

```
**Behavior**
* Scan K8s resources and Vault policies for violations
* Report P1–P7 matrix per cluster
* Output `/reports/selfhost_policy_audit.json`

---

## Pre-Check (Embedded)
```

python - <<'PY' > /reports/G.3_precheck.json 2>&1
import os,json
r={}
for k in ["K8S_CONTEXT","LOCAL_REGISTRY_URL","VAULT_PRIMARY_ADDR"]:
 r[k]=("SET" if os.getenv(k) else "MISSING")
r["decision"]="PROCEED" if r["K8S_CONTEXT"]=="SET" else "PROCEED_SIMULATION"
print(json.dumps(r,indent=2))
PY

```

---

## Integration Test
```

pytest -q tests/integration/test_G.3_end2end.py > /reports/logs/G.3_end2end.log 2>&1 || true
curl -s [http://localhost:8600/health](http://localhost:8600/health) > /reports/G.3_health.json || true

```

---

## Expected Outputs
```

/reports/G.3.*.md
/reports/logs/G.3.*.log
/reports/G.3_precheck.json
/reports/selfhost_policy_audit.json
/reports/PhaseG.3_Snapshot.json

```

---

## Failure Handling
* Missing K8s context → auto-simulate nodes  
* Registry push error → skip and log digest  
* Vault unreachable → mark as SYNC_SIMULATED  
* Never expose secrets in logs (<REDACTED>)

---

## Verification Criteria
✅ All service health endpoints return 200  
✅ `cluster_topology.json` exists  
✅ Vault sync log written  
✅ Policy audit passes P1–P7  
✅ Helm chart rendered successfully  

---

## Completion Rules
When all tasks succeed or simulate successfully:  
* Generate snapshot `reports/PhaseG.3_Snapshot.json`  
* Tag repo locally → `v7.2.0-phaseG.3`  
* Merge branches to `prod-review/PhaseG.3-Finalization`

---

## Embedded Agent Prompt
```

You are the ATOM coding agent. Execute Phase G.3 per this file. Run precheck. If infra missing → set SIMULATION_MODE=true. Implement tasks G.3.1→G.3.6, generate reports, tests, and snapshot. Do not push or open PRs. Upon success, recommend tag v7.2.0-phaseG.3.

```

---

## Tag Recommendation  
`v7.2.0-phaseG.3` — Self-Hosting Topology & Cluster Orchestration Complete

---

```

---

**Result:**
Running this file will let your ATOM agent autonomously build or simulate a full **self-hosting environment**, verifying Helm templates, Vault mirrors, and policy compliance—without external GitHub automation.


