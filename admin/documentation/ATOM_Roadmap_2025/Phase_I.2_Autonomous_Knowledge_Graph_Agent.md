Here is the complete **agent-ready `.md` file** for **Phase I.2 — Autonomous Knowledge Graph**, formatted for direct execution by your ATOM Agent.
Paste this file verbatim into:
📄 `/docs/Phase_I.2_Autonomous_Knowledge_Graph_Agent.md`

---

```markdown
# Phase I.2 — Autonomous Knowledge Graph (Agent-Ready .md)

**Objective**  
Extend the ATOM Global Intelligence Fabric into a self-organizing, AI-driven **Knowledge Graph (KG)** connecting data, models, policies, and outcomes.  
Implements federated ontology reasoning, dynamic relationship inference, semantic lineage tracking, and continuous learning across multi-region and quantum-neural layers.

**Version:** v9.1.0-phaseI.2  
**Branch prefix (local):** `prod-feature/I.2.<task>`  
**Mode:** Autonomous execution with `SIMULATION_MODE` fallback.  

---

## Environment Variables (required)

```

POSTGRES_DSN
VAULT_ADDR
COSIGN_KEY_PATH
GLOBAL_REGISTRY_URL
MODEL_STORE_URL
POLICY_HUB_URL
NEURAL_FABRIC_URL
QUANTUM_COORD_URL
PROM_URL
SIMULATION_MODE
GRAPH_BACKEND_URL

```

If any are missing, agent must set `SIMULATION_MODE=true` and continue in mock mode.

---

## Scope & Deliverables

**Primary Goal:** Create a **distributed semantic knowledge layer** that connects:
- Data features (from I.1)
- Models (from H.2–H.5)
- Policies (from G.5 & H.4)
- Outcomes (scorecards, audits, optimizations)

**Deliverables**
- 6 Knowledge Graph microservices
- Graph database schema + ontology builder
- Federated reasoning engine
- Lineage tracker & explainability API
- Semantic inference router
- Integration tests & reports

---

## High-Level Tasks (I.2.1 → I.2.6)

| ID | Task | Goal |
|----|------|------|
| I.2.1 | Graph Core Service | Foundation schema, CRUD for nodes/edges |
| I.2.2 | Ontology Builder | Define & evolve global data-model-policy ontology |
| I.2.3 | Lineage Tracker | Track data/model/policy lineage across time |
| I.2.4 | Semantic Reasoner | AI-driven relationship inference engine |
| I.2.5 | Explainability & Query API | Human-readable KG exploration & traceability |
| I.2.6 | Graph Integrator | Connect Global Fabric, Policy Hub, and Federation |

---

## Directory Structure

```

services/graph-core/
services/ontology-builder/
services/lineage-tracker/
services/semantic-reasoner/
services/explainability-api/
services/graph-integrator/
infra/sql/i2_graph_schema.sql
docs/policies/knowledge_graph_policy.md
tests/integration/test_I.2_end2end.py
reports/

```

Each service: `main.py`, `requirements.txt`, `Dockerfile`, `config.example.yaml`, `tests/`.

---

## Task Details

### I.2.1 — Graph Core Service
**Files**
```

services/graph-core/main.py
services/graph-core/schema.py
services/graph-core/tests/test_core.py
reports/I.2.1_graph_core.md

```

**Endpoints**
- `POST /graph/node` `{type, data, meta}`
- `POST /graph/edge` `{source, target, relation, confidence}`
- `GET /graph/{id}` → Node metadata
- `GET /health`, `GET /metrics`

**Behavior**
- Use Postgres or Neo4j mock for graph structure.
- Record SHA256 hash for immutability.
- Enforce tenant isolation (P5) and anonymization (P1).

---

### I.2.2 — Ontology Builder
**Files**
```

services/ontology-builder/main.py
services/ontology-builder/ontology.py
services/ontology-builder/tests/test_ontology.py
reports/I.2.2_ontology_builder.md

```

**Endpoints**
- `POST /ontology/define` `{namespace, entities[], relations[], constraints[]}`
- `GET /ontology/schema` list active ontology versions

**Behavior**
- Cosign-sign ontology manifests (P2).
- Auto-version changes; enforce approval workflow in prod (P3).

---

### I.2.3 — Lineage Tracker
**Files**
```

services/lineage-tracker/main.py
services/lineage-tracker/tracker.py
services/lineage-tracker/tests/test_tracker.py
reports/I.2.3_lineage_tracker.md

```

**Behavior**
- Store lineage edges `{source_type, source_id, target_type, target_id, event_time}`.
- Periodically compute lineage completeness score.
- Generate audit log entries (P4, P7).

---

### I.2.4 — Semantic Reasoner
**Files**
```

services/semantic-reasoner/main.py
services/semantic-reasoner/reasoner.py
services/semantic-reasoner/tests/test_reasoner.py
reports/I.2.4_semantic_reasoner.md

```

**Behavior**
- Infer new edges from graph statistics + ML.
- Use transformer embeddings or symbolic rules (mocked in simulation).
- Confidence threshold default 0.8.
- Log reasoning steps for explainability (P4).

---

### I.2.5 — Explainability & Query API
**Files**
```

services/explainability-api/main.py
services/explainability-api/query.py
services/explainability-api/tests/test_query.py
reports/I.2.5_explainability_api.md

```

**Endpoints**
- `GET /explain/{id}` → Trace data/model/policy lineage
- `POST /query` → Semantic search by entity type or relation

**Behavior**
- Provide human-readable lineage explanations.
- Sanitize sensitive data (P1).
- Expose `/metrics` for query latency.

---

### I.2.6 — Graph Integrator
**Files**
```

services/graph-integrator/main.py
services/graph-integrator/sync.py
services/graph-integrator/tests/test_sync.py
reports/I.2.6_graph_integrator.md

```

**Behavior**
- Sync graph metadata from:
  - Global Fabric (I.1)
  - Policy Hub (G.5)
  - Governance AI (H.4)
- Verify cosign signatures (P2).
- Merge lineage edges and ontologies.

---

## Precheck (agent-run)

```

mkdir -p reports/logs
python - <<'PY' > reports/I.2_precheck.json
import os,json
r={k:('SET' if os.getenv(k) else 'MISSING') for k in ['POSTGRES_DSN','VAULT_ADDR','COSIGN_KEY_PATH','GRAPH_BACKEND_URL']}
r['SIMULATION_MODE']=os.getenv('SIMULATION_MODE','true')
r['decision']='PROCEED' if r['POSTGRES_DSN']=='SET' else 'PROCEED_SIMULATION'
print(json.dumps(r,indent=2))
PY

```

Decision:
- `PROCEED_SIMULATION` if any critical missing.
- `PROCEED` only if DB + Vault available.

---

## Verification Commands

```

pytest -q tests/integration/test_I.2_end2end.py > /reports/logs/I.2_end2end.log 2>&1 || true
curl -s [http://localhost:9101/health](http://localhost:9101/health) > /reports/I.2_health.json || true

```

Integration test includes:
- Graph node creation
- Ontology definition
- Lineage link formation
- Reasoner inference check
- Explainability query
- Sync from global fabric mock

---

## Reporting

Each `/reports/I.2.x_*.md` includes:
- Branch + SHA
- SIMULATION_MODE flag
- Test results
- Policy compliance (P1–P7)
- Summary of inferred edges, ontology versions, lineage completeness
- Blockers and remediation plan

Final snapshot:
```

python scripts/generate_phase_snapshot.py

```
→ `/reports/PhaseI.2_Snapshot.json`

---

## Policy Summary

| Policy | Enforcement | Notes |
|--------|--------------|-------|
| P1 | Data anonymization | All graph data hashed or aggregated |
| P2 | Signature verification | Ontology + sync manifests |
| P3 | Safe execution | No auto-merge without approval |
| P4 | Observability | Full metrics and audit logs |
| P5 | Multi-Tenancy | Namespace per tenant |
| P6 | Performance | Query latency < 500ms |
| P7 | Resilience | Rollback snapshots every 24h |

---

## Agent Execution Sequence

1. Run precheck → decide SIMULATION or full.
2. Implement I.2.1 → I.2.6 sequentially.
3. Run tests & verifications.
4. Generate reports, logs, and snapshot.
5. Tag version: `v9.1.0-phaseI.2`
6. Do not push or create PRs automatically.

---

## Embedded Agent Prompt

```

You are the ATOM coding agent. Execute Phase I.2 per /docs/Phase_I.2_Autonomous_Knowledge_Graph_Agent.md. Run precheck. If infra missing, set SIMULATION_MODE=true. Implement I.2.1→I.2.6 services, tests, and reports. Verify ontology sync, lineage tracking, and inference. Commit locally per task, generate snapshot, and tag v9.1.0-phaseI.2. Do not push remotely. Never log secrets.

```

---
**End of File — Phase I.2 Autonomous Knowledge Graph Agent Plan**
```

---

