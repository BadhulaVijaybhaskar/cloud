Below is the **production hardening blueprint** — formatted for direct use by your coding agent after MVP verification.
Save this file as:

> `/docs/NakshaCloud_Production_Upgrade.md`

It lists every subsystem upgrade, infra requirement, and security rule needed to move **Naksha Cloud** from MVP+ to **stable production**.

---

# Naksha Cloud — Production Upgrade Blueprint

*For agent execution after MVP validation*

---

## **1. Infrastructure Tier (Cloud-native)**

### Required Cloud Resources

| Resource                       | Example Provider                                  | Purpose                                           |
| ------------------------------ | ------------------------------------------------- | ------------------------------------------------- |
| **Managed Kubernetes Cluster** | AWS EKS / GCP GKE / Azure AKS                     | Host LangGraph, VectorDB, Vault, Observability    |
| **Postgres (HA)**              | AWS RDS / GCP Cloud SQL                           | Core transactional DB with PITR and read replicas |
| **Object Storage**             | AWS S3 / GCP Storage                              | Versioned file storage, logs, snapshots           |
| **VectorDB (Managed)**         | Zilliz Cloud (Milvus) / Pinecone / Weaviate Cloud | Scalable embeddings search                        |
| **Load Balancer (L7)**         | ALB / Ingress Gateway                             | Public API entrypoint                             |
| **DNS + TLS**                  | Cloudflare / Route53                              | Domain and SSL management                         |
| **Secrets Management (HSM)**   | HashiCorp Vault + KMS seal                        | Key security and rotation                         |
| **Observability**              | Managed Grafana / Prometheus Stack                | Metrics, logs, traces                             |
| **Backup Storage**             | S3/Coldline                                       | Nightly DB + Object + Vector backups              |

---

## **2. Network & Security Architecture**

| Component                        | Requirement                                            |
| -------------------------------- | ------------------------------------------------------ |
| **Private Subnets**              | Place DBs, Vault, and VectorDB in non-public networks  |
| **VPC Peering / Internal LB**    | Internal communication between cluster and DBs         |
| **Network Policies (K8s)**       | Limit traffic namespace-to-namespace                   |
| **TLS Everywhere**               | Cert-manager for internal + public endpoints           |
| **WAF / Firewall Rules**         | Block non-HTTPS and unverified sources                 |
| **Zero Trust Auth (OIDC)**       | Every service must authenticate via JWT or Vault token |
| **HSM or KMS Sealing for Vault** | Cloud KMS integration for secure unseal                |
| **Image Provenance**             | Use signed Docker images (Cosign, Sigstore)            |
| **Least Privilege IAM**          | Granular IAM for S3, DB, and Vault roles               |

---

## **3. Data Layer Hardening**

| Service                   | Required Enhancements                                                   |
| ------------------------- | ----------------------------------------------------------------------- |
| **Postgres**              | Multi-AZ deployment, automated snapshots, PITR (point-in-time recovery) |
| **VectorDB**              | Persistent volumes + replication factor ≥ 2                             |
| **MinIO / S3**            | Enable versioning + lifecycle policy + encryption at rest               |
| **Vault**                 | Enable audit logging + policies per microservice                        |
| **LangGraph State Store** | Move job metadata to managed DB, enable backup job                      |

---

## **4. LangGraph Orchestrator Scaling**

| Upgrade                            | Description                           |
| ---------------------------------- | ------------------------------------- |
| **Horizontal Autoscaling**         | HPA based on queue depth & CPU        |
| **Pod Disruption Budgets**         | Maintain availability during updates  |
| **Dedicated Namespace**            | `langgraph-prod` for isolation        |
| **Tracing**                        | OpenTelemetry export to Grafana Tempo |
| **Circuit Breaker / Retry Policy** | Use NATS durable consumers            |
| **Vault Auth Renewal**             | Auto-renew service tokens every hour  |

---

## **5. Observability Stack (Production-Grade)**

| Component          | Requirement                                                     |
| ------------------ | --------------------------------------------------------------- |
| **Prometheus**     | Retention ≥ 15 days, remote-write to managed TSDB               |
| **Grafana**        | Dashboards for DB latency, LangGraph cost, embedding throughput |
| **Loki**           | Persistent volume + label filtering by service                  |
| **Tempo / Jaeger** | Distributed tracing for LangGraph workflows                     |
| **AlertManager**   | Alerts to Slack / PagerDuty                                     |
| **Cost Exporter**  | Prometheus job to track compute + token usage                   |

---

## **6. CI/CD and Deployment Automation**

### GitHub Actions / GitLab CI Additions

| Step                   | Purpose                          |
| ---------------------- | -------------------------------- |
| `terraform plan/apply` | Infrastructure provisioning      |
| `helm upgrade`         | Deploy updated services          |
| `policy scan`          | Check OPA/Gatekeeper compliance  |
| `image sign`           | Cosign image before deploy       |
| `integration test`     | Run health + RAG pipeline tests  |
| `notify`               | Post deployment summary to Slack |

### Deployment Strategy

* **Staging environment** mirrors prod but smaller.
* **Blue/Green or Canary deploys** via Helm hooks.
* **Rollback automation** on failed health check.

---

## **7. Compliance & Audit**

| Control             | Implementation                               |
| ------------------- | -------------------------------------------- |
| **Access Logs**     | Vault, DB, Object store logs → Loki          |
| **Data Encryption** | AES-256 for data, TLS 1.3 for transit        |
| **Secret Rotation** | 30-day rotation via Vault policy             |
| **RBAC Auditing**   | Export roles & permissions snapshot daily    |
| **Change Control**  | GitOps with signed commits                   |
| **API Audit Trail** | Every job / RAG query logged with request id |

---

## **8. Cost & Resource Optimization**

| Area                  | Practice                                               |
| --------------------- | ------------------------------------------------------ |
| **Compute**           | Use autoscaling node pools; spot instances for workers |
| **Storage**           | Cold storage for logs older than 30 days               |
| **Vector Index**      | Dynamic index compaction + caching                     |
| **API Costs**         | Switch to Hugging Face inference endpoints             |
| **Metrics Retention** | Use remote storage (Thanos / Cortex)                   |

---

## **9. Production Backups**

| Target                   | Frequency        | Retention  | Tool              |
| ------------------------ | ---------------- | ---------- | ----------------- |
| Postgres                 | Daily            | 7 days     | pg_dump + cronjob |
| VectorDB                 | Daily            | 7 days     | Milvus backup     |
| Vault policies & secrets | Weekly           | 30 days    | Vault snapshot    |
| Object store             | Lifecycle policy | 30–90 days | S3 versioning     |
| Grafana dashboards       | Weekly           | Git export |                   |

---

## **10. Incident Recovery Plan**

1. Monitor alerts (CPU, latency, errors).
2. On service failure → auto-restart via K8s health probes.
3. On data loss → restore from latest backup snapshot.
4. Rotate credentials post-incident.
5. Generate audit report using Vault + Loki logs.
6. Validate recovery through automated smoke tests.

---

## **11. Domains & SSL**

* Use Cloudflare or Route53 for DNS.
* Use cert-manager to auto-renew TLS certificates via Let’s Encrypt.
* Enforce HTTPS redirect for all ingress routes.
* Store certificates in Vault (read-only for services).

---

## **12. Checklist before public release**

| Check                                   | Expected Result |
| --------------------------------------- | --------------- |
| HPA scales pods automatically           | ✅               |
| Vault unseal via KMS works              | ✅               |
| Prometheus → Grafana dashboards visible | ✅               |
| LangGraph jobs traceable in Tempo       | ✅               |
| RDS snapshots verified                  | ✅               |
| S3 versioning enabled                   | ✅               |
| JWT & OAuth auth tested                 | ✅               |
| Canary deployment rollback verified     | ✅               |
| Security scan passes (Trivy/OPA)        | ✅               |

---

## **13. Final Deliverables**

| Artifact                             | Directory                | Description               |
| ------------------------------------ | ------------------------ | ------------------------- |
| `terraform/production/`              | Infrastructure modules   | Cloud IaC                 |
| `helm-values/prod/`                  | Helm values tuned for HA | Production-ready configs  |
| `vault/policies/`                    | Fine-grained roles       | Secure access control     |
| `.github/workflows/prod-deploy.yaml` | CI/CD pipeline           | Auto-deploy to production |
| `monitoring/`                        | Dashboards + alerts      | Observability stack       |

---

## **14. Optional Enterprise Add-ons**

| Add-on                                           | Benefit                  |
| ------------------------------------------------ | ------------------------ |
| **OIDC integration with corporate SSO**          | Unified user management  |
| **Dedicated model gateway (LangGraph + Triton)** | Local inference hosting  |
| **Multi-tenant billing engine**                  | Metered usage reports    |
| **Federated Observability (Thanos)**             | Cross-region metrics     |
| **Infra as Code drift detection (Atlantis)**     | Auto plan/merge workflow |

---

## **Summary**

After MVP testing, production requires:

* Managed infrastructure,
* Enforced security + backup policies,
* Full observability + compliance logging,
* Automated deployments with rollback.

When the MVP passes validation, run:

> `terraform workspace new production`
> `helm upgrade --install -f helm-values/prod/*`

Naksha Cloud will then operate as a **resilient, AI-native, multi-tenant backend platform** ready for external users and enterprise onboarding.


f