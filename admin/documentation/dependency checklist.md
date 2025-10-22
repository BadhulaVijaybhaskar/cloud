Yes. Below is a **complete and minimal dependency checklist** for running and testing the current **Naksha Cloud MVP+ stack** (with LangGraph, VectorDB, Vault, Observability).
It’s written in the same **agent-readable format**, so you can paste it into your `/docs/` folder as:

> `/docs/NakshaCloud_Testing_Keys.md`

---

# Naksha Cloud — Required Keys, Tokens, and External Sources (for MVP+ testing)

---

## 1. **Postgres**

**Purpose:** Primary data store for LangGraph, Hasura, and project metadata.
**Required:**

| Variable       | Example                                             | Source                   | Notes                             |
| -------------- | --------------------------------------------------- | ------------------------ | --------------------------------- |
| `DATABASE_URL` | `postgres://naksha_user:naksha_pass@db:5432/naksha` | internal Postgres or RDS | must exist before LangGraph boots |

---

## 2. **VectorDB (Milvus or Weaviate)**

**Purpose:** Store and query embeddings for RAG.
**Required:**

| Variable         | Example               | Source                       | Notes                            |
| ---------------- | --------------------- | ---------------------------- | -------------------------------- |
| `VECTOR_DB_URL`  | `http://milvus:19530` | Helm-deployed Milvus service | internal only                    |
| `VECTOR_DB_USER` | optional              | local                        | not required unless auth enabled |

---

## 3. **Object Storage (MinIO or S3)**

**Purpose:** Object storage for file uploads and backups.
**Required:**

| Variable        | Example             | Source                     | Notes |
| --------------- | ------------------- | -------------------------- | ----- |
| `S3_ENDPOINT`   | `http://minio:9000` | internal MinIO             |       |
| `S3_ACCESS_KEY` | `minio`             | MinIO credentials          |       |
| `S3_SECRET_KEY` | `minio123`          | MinIO credentials          |       |
| `S3_BUCKET`     | `naksha-files`      | created via startup script |       |

---

## 4. **Vault / Secrets Management**

**Purpose:** Central secret store and short-lived credentials.
**Required:**

| Variable      | Example                                   | Source               | Notes                      |
| ------------- | ----------------------------------------- | -------------------- | -------------------------- |
| `VAULT_ADDR`  | `https://vault.default.svc.cluster.local` | Helm Vault install   | internal endpoint          |
| `VAULT_ROLE`  | `langgraph-role`                          | created during setup | must match Kubernetes role |
| `VAULT_TOKEN` | obtained via SA login                     | auto-generated       | only for local tests       |

---

## 5. **AI & Embeddings API**

**Purpose:** Generate vector embeddings for text.
**Required:**

| Variable         | Example        | Source         | Notes                                    |
| ---------------- | -------------- | -------------- | ---------------------------------------- |
| `OPENAI_API_KEY` | `sk-xxxxx`     | OpenAI account | required for `embed.py` or RAG pipelines |
| *Alternative*    | `HF_API_TOKEN` | Hugging Face   | can replace OpenAI for local embeddings  |

---

## 6. **Realtime / Messaging**

**Purpose:** Job queue and live updates.
**Required:**

| Variable                  | Example            | Source          | Notes                    |
| ------------------------- | ------------------ | --------------- | ------------------------ |
| `NATS_URL`                | `nats://nats:4222` | NATS Helm chart |                          |
| `NATS_USER` / `NATS_PASS` | optional           | from chart      | required if auth enabled |

---

## 7. **Observability Stack**

**Purpose:** Metrics, logs, traces collection.
**Required:**

| Variable          | Example                                          | Source     | Notes                    |
| ----------------- | ------------------------------------------------ | ---------- | ------------------------ |
| `PROMETHEUS_ADDR` | `http://prometheus.monitoring.svc.cluster.local` | Prometheus | LangGraph pushes metrics |
| `GRAFANA_URL`     | `http://grafana.monitoring.svc.cluster.local`    | Grafana    | optional UI              |
| `LOKI_URL`        | `http://loki.monitoring.svc.cluster.local`       | Loki       | logs ingestion           |

---

## 8. **Auth / Supabase-style Identity (if enabled)**

**Purpose:** Developer or tenant authentication.
**Required:**

| Variable                 | Example               | Source               | Notes               |
| ------------------------ | --------------------- | -------------------- | ------------------- |
| `JWT_SECRET`             | random 32-char string | generated locally    | used by API Gateway |
| `OAUTH_GOOGLE_CLIENT_ID` | optional              | Google Cloud Console | for OAuth login     |
| `OAUTH_GOOGLE_SECRET`    | optional              | Google Cloud Console |                     |

---

## 9. **CI/CD & Deployment**

**Purpose:** Terraform + Helm automation.
**Required:**

| Variable                                      | Example           | Source         | Notes                        |
| --------------------------------------------- | ----------------- | -------------- | ---------------------------- |
| `GITHUB_TOKEN`                                | auto              | GitHub Actions | needed for workflow          |
| `KUBECONFIG_BASE64`                           | base64 kubeconfig | GitHub Secret  | connect Terraform to cluster |
| `TF_VAR_region`                               | `us-east-1`       | environment    | for cloud provider modules   |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | optional          | AWS            | only if using S3/RDS         |

---

## 10. **Optional Integrations**

| Integration   | Keys                          | Purpose                          |
| ------------- | ----------------------------- | -------------------------------- |
| Slack Webhook | `SLACK_WEBHOOK_URL`           | send LangGraph job notifications |
| HuggingFace   | `HF_API_TOKEN`                | alternative embedding source     |
| OpenTelemetry | `OTEL_EXPORTER_OTLP_ENDPOINT` | traces export                    |

---

## 11. **Checklist before testing**

| Check                                 | Expected Result |
| ------------------------------------- | --------------- |
| Postgres reachable via `DATABASE_URL` | ✅               |
| Milvus responding on port 19530       | ✅               |
| Vault pods running & unsealed         | ✅               |
| `vault auth list` shows `kubernetes/` | ✅               |
| LangGraph deployment ready            | ✅               |
| `GET /healthz` → 200 OK               | ✅               |
| `curl /metrics` shows counters        | ✅               |
| Grafana dashboards load               | ✅               |
| `docker compose ps` shows all healthy | ✅               |

---

## 12. **Security Reminder**

Never hard-code any secret keys in `.env` or Dockerfiles.
Store in Vault or GitHub Actions Secrets.

---

## 13. **Testing workflow**

1. Run `docker compose up -d` (for local dev) or apply Helm charts (cluster).
2. Run `infra/scripts/setup.sh` → seeds DB and buckets.
3. `POST /v1/jobs` (LangGraph) with `sample_rag.yaml`.
4. Check results in `vector` service and logs in Grafana/Loki.
5. Validate end-to-end latency and embedding success.

---
