Understood. Below is a single document — written in **coding-agent-friendly Markdown**, minimal English, structured with instructions, file paths, and task directives.
Save it as:

> `/docs/NakshaCloud_Extensions.md`

This file tells a coding agent exactly what to create, where, and why — to extend your existing `cloud` repo with **LangGraph**, **VectorDB**, **Vault**, **HA**, and **Observability**.

---

# Naksha Cloud – Core Extensions Implementation Plan

*version: agent-ready doc, October 2025*

---

## 1. LangGraph Orchestration Component

**Goal:** add a scalable AI/data orchestration layer inside the cluster.

### Directory

```
services/langgraph/
  ├─ Dockerfile
  ├─ main.py
  ├─ requirements.txt
  ├─ graph_definitions/
  │   └─ sample_rag.yaml
  ├─ api/
  │   ├─ server.py
  │   └─ routes/
  │       ├─ jobs.py
  │       └─ graphs.py
```

### Agent Tasks

1. **Create container** using `python:3.11-slim`, expose port 8080.
2. **Install**: `fastapi`, `uvicorn`, `langgraph`, `psycopg2`, `redis`, `pydantic`.
3. **Implement endpoints**

   * `POST /v1/jobs` → enqueue workflow
   * `GET  /v1/jobs/{id}` → return status
4. **Connect Postgres** via `DATABASE_URL` env.
5. **Use Redis/NATS** for queue.
6. **Read graph YAML** from `graph_definitions/`, parse with LangGraph API.
7. **Emit logs/metrics** to Prometheus via `/metrics`.

### Deployment

* Helm chart at `infra/helm/langgraph/`
* Add Terraform module call:

  ```hcl
  module "langgraph" {
    source = "./terraform/modules/langgraph-orchestrator"
    env = {
      DATABASE_URL  = module.postgres.db_url
      VECTOR_DB_URL = module.vector.endpoint
      VAULT_ADDR    = module.vault.addr
    }
  }
  ```

---

## 2. VectorDB + Embeddings Pipeline

**Goal:** enable semantic search and AI-retrieval inside Naksha.

### Directory

```
services/vector/
  ├─ docker-compose.override.yml
  ├─ milvus/
  │   └─ helm-values.yaml
  ├─ ingestion/
  │   ├─ ingest.py
  │   └─ embed.py
```

### Agent Tasks

1. Deploy **Milvus** via Helm (`infra/helm/milvus/`).
2. Implement `ingest.py`: read from Postgres → chunk text → call embed API.
3. Implement `embed.py`:

   ```python
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
   emb = client.embeddings.create(model="text-embedding-3-small", input=text)
   ```
4. Write vectors to Milvus using `pymilvus`.
5. Expose `/v1/vector/query` endpoint through FastAPI → returns nearest-neighbors.
6. Integrate with LangGraph node `type: vector.upsert` and `type: vector.query`.

---

## 3. Vault / HSM Secrets Integration

**Goal:** remove plaintext secrets and enforce scoped credentials.

### Directory

```
infra/vault/
  ├─ helm-values.yaml
  ├─ policies/
  │   ├─ langgraph.hcl
  │   ├─ vector.hcl
  │   └─ postgres.hcl
  └─ roles/
      └─ langgraph-role.json
```

### Agent Tasks

1. Install **Vault Helm chart** into `vault` namespace.
2. Enable `auth/kubernetes` method.
3. Create roles:

   ```bash
   vault write auth/kubernetes/role/langgraph-role \
     bound_service_account_names=langgraph-sa \
     policies=langgraph \
     ttl=1h
   ```
4. Define policies (`policies/langgraph.hcl`) granting read on `secret/data/langgraph/*`.
5. Inject secrets via Vault Agent Injector or CSI driver.
6. Update Helm charts to use `VAULT_ADDR` and `VAULT_ROLE` envs.

---

## 4. High Availability & Backups

**Goal:** resilient cluster, DB, and storage.

### Agent Tasks

1. Postgres: enable replication or use managed RDS with PITR.
2. NATS: deploy with 3 JetStream pods.
3. MinIO: 4-node distributed mode.
4. Daily backups → S3 bucket via `infra/scripts/backup.sh`.
5. Add Terraform cronjob resource for snapshot automation.
6. Expose health probes for LangGraph and VectorDB.

---

## 5. Observability Stack

**Goal:** central metrics, logs, traces.

### Directory

```
infra/helm/observability/
  ├─ prometheus-values.yaml
  ├─ grafana-values.yaml
  ├─ loki-values.yaml
```

### Agent Tasks

1. Deploy Prometheus, Grafana, Loki (Helm charts).
2. Scrape targets: LangGraph, VectorDB, Postgres exporter, NATS.
3. Add Grafana dashboards for:

   * LangGraph job latency and cost
   * Vector query QPS
   * DB latency
4. Enable Loki log collection from all namespaces with label `app=naksha`.

---

## 6. CI/CD Enhancements

**Goal:** automatic infra deploy and validation.

### Directory

```
.github/workflows/infra-ci.yaml
```

### Agent Tasks

1. Terraform plan → apply with OIDC credentials.
2. Helm upgrade for LangGraph, VectorDB, Vault.
3. Run smoke tests post-deploy:

   ```bash
   curl -f http://langgraph.<domain>/healthz
   curl -f http://vector.<domain>/metrics
   ```

---

## 7. Deliverables Summary

| Feature                 | Directory                   | Output                           |
| ----------------------- | --------------------------- | -------------------------------- |
| LangGraph orchestration | `services/langgraph/`       | FastAPI service + Helm chart     |
| VectorDB & embeddings   | `services/vector/`          | Milvus + ingestion scripts       |
| Vault integration       | `infra/vault/`              | Helm + policies + roles          |
| HA & backups            | `infra/scripts/`            | cron + replication configs       |
| Observability           | `infra/helm/observability/` | Prometheus, Grafana, Loki        |
| CI/CD                   | `.github/workflows/`        | Terraform + Helm deploy pipeline |

---

## 8. Environment Variables (shared)

| Name              | Example                                   | Purpose        |
| ----------------- | ----------------------------------------- | -------------- |
| `DATABASE_URL`    | `postgres://user:pass@db:5432/naksha`     | primary DB     |
| `VECTOR_DB_URL`   | `http://milvus:19530`                     | vector search  |
| `VAULT_ADDR`      | `https://vault.default.svc.cluster.local` | secrets API    |
| `VAULT_ROLE`      | `langgraph-role`                          | service auth   |
| `OPENAI_KEY`      | `sk-xxxx`                                 | embeddings API |
| `PROMETHEUS_ADDR` | `http://prometheus.monitoring.svc`        | metrics push   |

---

## 9. Execution Order (agent flow)

1. Clone repo and create all folders above.
2. Commit initial Dockerfiles + Helm charts.
3. Apply Terraform modules for Postgres, VectorDB, Vault.
4. Deploy observability stack.
5. Verify LangGraph health at `/healthz`.
6. Test sample RAG workflow via:

   ```bash
   curl -X POST http://langgraph/api/v1/jobs -d @graph_definitions/sample_rag.yaml
   ```
7. Push metrics → confirm in Grafana.



