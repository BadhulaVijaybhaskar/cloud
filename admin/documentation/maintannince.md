Here is a factual cost and dependency breakdown for **Naksha Cloud in full production**.
It separates **mandatory core APIs**, **optional AI integrations**, and **estimated monthly maintenance cost** for a lean single-region deployment.
Values assume standard public-cloud pricing as of late 2025.

---

## **1. Core Maintenance Cost Estimate (monthly)**

| Component                       | Deployment                             | Purpose                                       | Est. Cost USD / month (optimized) |
| ------------------------------- | -------------------------------------- | --------------------------------------------- | --------------------------------- |
| **Kubernetes cluster**          | 3 × t3.medium nodes on EKS / GKE / AKS | Run LangGraph, VectorDB, Vault, Observability | ≈ $60 – $80                       |
| **Postgres (RDS / Cloud SQL)**  | db.t4g.small, 20 GB storage            | Transactional + LangGraph state               | ≈ $30 – $40                       |
| **Object Storage (S3 / GCS)**   | 50 GB data + 100 GB backup             | Buckets, logs, snapshots                      | ≈ $5 – $10                        |
| **VectorDB**                    | Self-hosted Milvus on cluster          | Embedding + search                            | ≈ $20 (compute + storage)         |
| **Vault OSS + KMS seal**        | Pod + KMS key ($1/mo key fee)          | Secrets management                            | ≈ $5 – $10                        |
| **NATS JetStream**              | On-cluster HA (3 pods)                 | Realtime / queues                             | ≈ $5                              |
| **Prometheus + Grafana + Loki** | On-cluster (2 vCPU, 4 GB)              | Metrics, logs UI                              | ≈ $10 – $15                       |
| **Backup S3 storage**           | Lifecycle (30 days)                    | Snapshots and archives                        | ≈ $2 – $5                         |
| **Domain + SSL certs**          | Cloudflare / Route53 + Let’s Encrypt   | HTTPS + DNS                                   | ≈ $1 – $2                         |
| **Misc. egress + overhead**     | —                                      | Network transfer + reserved costs             | ≈ $10 – $15                       |

**➡ Total ≈ $150 – $200 / month**
All open-source components, no vendor-locked services, moderate load (< 100 concurrent jobs).

---

## **2. Optional / Pay-per-use APIs**

| API / Service                   | Purpose                        | Pricing (typical 2025)                                           | When to Enable                                       |
| ------------------------------- | ------------------------------ | ---------------------------------------------------------------- | ---------------------------------------------------- |
| **OpenAI API**                  | Embeddings + LLM generation    | ≈ $0.10 / 1K embeddings · $0.002 / 1K tokens (text-small models) | If precise semantic search or text generation needed |
| **Hugging Face Inference API**  | Local or hosted model endpoint | Free (local) · Pay-as-you-go for HF Hub Space                    | For private model hosting                            |
| **Pinecone / Weaviate Cloud**   | Managed VectorDB               | ≈ $40 – $120 / month (starting tier)                             | If you avoid self-hosting Milvus                     |
| **Cloud KMS (AWS/GCP)**         | Vault seal + key rotation      | $1 per key + $0.03 per 10 K ops                                  | For compliance and auto unseal                       |
| **Slack / PagerDuty API**       | Ops alerts                     | Free / $10 per seat                                              | For alert routing                                    |
| **Sentry / Datadog**            | Application monitoring         | $15 – $50 / month                                                | Replace or augment Grafana/Loki                      |
| **Email / OTP (SendGrid, SES)** | User auth emails               | Free tier → $15 +                                                | If you expose Auth module                            |

---

## **3. Minimal API Key Inventory (production)**

| Variable                                      | Provider                   | Mandatory (✅) / Optional (⚪) |
| --------------------------------------------- | -------------------------- | ---------------------------- |
| `OPENAI_API_KEY`                              | OpenAI LLM / Embeddings    | ⚪                            |
| `HF_API_TOKEN`                                | Hugging Face               | ⚪                            |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | AWS infra (S3 / RDS / KMS) | ✅ (if on AWS)                |
| `VAULT_TOKEN` / `VAULT_ROLE`                  | Vault access               | ✅                            |
| `JWT_SECRET`                                  | API Gateway Auth           | ✅                            |
| `GITHUB_TOKEN`                                | CI/CD Actions              | ✅                            |
| `SLACK_WEBHOOK_URL`                           | Ops notifications          | ⚪                            |
| `OTEL_EXPORTER_OTLP_ENDPOINT`                 | OpenTelemetry traces       | ⚪                            |
| `PROMETHEUS_ADDR`, `GRAFANA_URL`, `LOKI_URL`  | Observability stack links  | ✅ (local) / ⚪ (cloud)        |

---

## **4. Cost Scaling Rules**

| Load Factor                             | Typical Change                        | New Cost              |
| --------------------------------------- | ------------------------------------- | --------------------- |
| + 5× traffic (500 active users)         | + 2 nodes + bigger DB + object growth | ≈ $300 – $350 / month |
| + 10× LangGraph jobs                    | Scale worker pool + NATS cluster      | + $50 – $80           |
| Add OpenAI RAG queries (100 K requests) | Token usage                           | + $20 – $40           |
| Multi-region failover                   | Second cluster + replicated storage   | ≈ 2× baseline         |

---

### **Summary**

| Environment                  | APIs needed                               | Approx Cost           |
| ---------------------------- | ----------------------------------------- | --------------------- |
| **Local MVP**                | none (OSS only)                           | $0                    |
| **Single-region Production** | Vault, KMS, RDS, S3, Grafana              | ≈ $150 – $200 / month |
| **Full enterprise prod**     | + OpenAI/Pinecone + HSM + monitoring SaaS | ≈ $350 – $600 / month |

---

**Bottom line:**

* You can run Naksha Cloud production reliably for **under $200/month** using open-source and managed base tiers.
* Only **embedding/LLM APIs** (OpenAI, HF) add variable cost.
* All other components are predictable monthly compute + storage.
