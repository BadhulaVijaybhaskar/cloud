# Phase J.3 — Marketplace (Agent-Ready .md)

**Objective**  
Build a comprehensive AI-powered marketplace for ATOM Cloud services, templates, and integrations. Enable developers to discover, deploy, and monetize cloud solutions with automated quality scoring, security validation, and neural recommendation engine.

**Version:** v10.3.0-phaseJ.3  
**Branch prefix (local):** `prod-feature/J.3.<task>`  
**Mode:** Autonomous execution with `SIMULATION_MODE` fallback

---

## Environment Variables (required)

```
POSTGRES_DSN
VAULT_ADDR
COSIGN_KEY_PATH
GLOBAL_REGISTRY_URL
MARKETPLACE_API_URL
PAYMENT_GATEWAY_URL
AI_SCORING_URL
NEURAL_FABRIC_URL
SIMULATION_MODE
S3_BUCKET_URL
STRIPE_SECRET_KEY
```

If any are missing, agent must set `SIMULATION_MODE=true` and continue in mock mode.

---

## Policies enforced (inherit P1–P7)

- P1 Data Privacy: All marketplace data anonymized, vendor PII protected
- P2 Secrets & Signing: All marketplace packages cosign-verified
- P3 Execution Safety: Auto-deployment requires approval workflow
- P4 Observability: Full metrics on downloads, ratings, revenue
- P5 Multi-Tenancy: Vendor-scoped namespaces and billing isolation
- P6 Performance Budget: Search results < 200ms, package install < 30s
- P7 Resilience & Recovery: Package rollback and version management

---

## High-level tasks (J.3.1 → J.3.6)

| ID | Task | Goal |
|----|------|------|
| J.3.1 | Marketplace Core API | Package registry, search, metadata management |
| J.3.2 | AI Quality Scorer | Neural scoring for security, performance, reliability |
| J.3.3 | Payment & Billing Engine | Stripe integration, revenue sharing, analytics |
| J.3.4 | Package Deployment Service | One-click install, dependency resolution |
| J.3.5 | Vendor Portal | Publisher dashboard, analytics, revenue tracking |
| J.3.6 | Marketplace UI | Discovery interface, reviews, recommendations |

---

## Files & dirs to create (exact list)

```
services/marketplace-api/
services/ai-quality-scorer/
services/payment-engine/
services/package-deployer/
services/vendor-portal/
ui/marketplace/
infra/sql/j3_marketplace_schema.sql
tests/integration/test_J.3_end2end.py
docs/policies/marketplace_policy.md
reports/
```

Each service must include `main.py`, `requirements.txt`, `Dockerfile`, `config.example.yaml`, `tests/` and expose `/health` and `/metrics`.

---

## Task details (abbreviated — agent implements full stubs)

### J.3.1 — Marketplace Core API
**Branch:** `prod-feature/J.3.1-marketplace-api`  
**Files**
```
services/marketplace-api/main.py
services/marketplace-api/registry.py
services/marketplace-api/search.py
services/marketplace-api/tests/test_api.py
reports/J.3.1_marketplace_api.md
```
**Endpoints**
- `POST /packages/publish` {name, version, manifest, signature}
- `GET /packages/search?q={query}&category={cat}` 
- `GET /packages/{id}` → Package details
- `POST /packages/{id}/install` → Trigger deployment
- `GET /health` `GET /metrics`
**Behavior**
- Validate cosign signatures on all packages (P2)
- Elasticsearch/PostgreSQL for search indexing
- Rate limiting and tenant isolation (P5)
**Verification**
```
pytest -q services/marketplace-api/tests/test_api.py > /reports/logs/J.3.1.log 2>&1 || true
curl -s -X POST http://localhost:9301/packages/publish -d '{"name":"test-pkg","version":"1.0.0"}' -H "Content-Type:application/json" > /reports/J.3.1_publish.json || true
```

### J.3.2 — AI Quality Scorer
**Branch:** `prod-feature/J.3.2-ai-scorer`  
**Files**
```
services/ai-quality-scorer/main.py
services/ai-quality-scorer/scorer.py
services/ai-quality-scorer/models.py
services/ai-quality-scorer/tests/test_scorer.py
reports/J.3.2_ai_quality_scorer.md
```
**Endpoints**
- `POST /score/package` {package_url, metadata}
- `GET /score/{package_id}` → Quality metrics
**Behavior**
- Security scan (Trivy/Grype integration)
- Performance benchmarking simulation
- Code quality analysis (complexity, coverage)
- Neural scoring algorithm (0-100 scale)
**Verification**
```
pytest -q services/ai-quality-scorer/tests/test_scorer.py > /reports/logs/J.3.2.log 2>&1 || true
curl -s -X POST http://localhost:9302/score/package -d '{"package_url":"test://pkg"}' -H "Content-Type:application/json" > /reports/J.3.2_score.json || true
```

### J.3.3 — Payment & Billing Engine
**Branch:** `prod-feature/J.3.3-payment-engine`  
**Files**
```
services/payment-engine/main.py
services/payment-engine/stripe_client.py
services/payment-engine/billing.py
services/payment-engine/tests/test_payment.py
reports/J.3.3_payment_engine.md
```
**Endpoints**
- `POST /billing/purchase` {package_id, user_id, payment_method}
- `GET /billing/revenue/{vendor_id}` → Revenue analytics
- `POST /billing/payout` → Vendor payouts
**Behavior**
- Stripe integration (mock in simulation)
- Revenue sharing (70% vendor, 30% platform)
- Automated monthly payouts
- Tax calculation and reporting
**Verification**
```
pytest -q services/payment-engine/tests/test_payment.py > /reports/logs/J.3.3.log 2>&1 || true
curl -s -X POST http://localhost:9303/billing/purchase -d '{"package_id":"pkg-1","amount":2999}' -H "Content-Type:application/json" > /reports/J.3.3_purchase.json || true
```

### J.3.4 — Package Deployment Service
**Branch:** `prod-feature/J.3.4-package-deployer`  
**Files**
```
services/package-deployer/main.py
services/package-deployer/deployer.py
services/package-deployer/dependency_resolver.py
services/package-deployer/tests/test_deployer.py
reports/J.3.4_package_deployer.md
```
**Endpoints**
- `POST /deploy/package` {package_id, target_workspace, config}
- `GET /deploy/status/{deployment_id}`
- `POST /deploy/rollback/{deployment_id}`
**Behavior**
- Helm chart deployment to Kubernetes
- Dependency resolution and conflict detection
- Health checks and rollback on failure
- Integration with ATOM orchestrator
**Verification**
```
pytest -q services/package-deployer/tests/test_deployer.py > /reports/logs/J.3.4.log 2>&1 || true
curl -s -X POST http://localhost:9304/deploy/package -d '{"package_id":"pkg-1","workspace":"ws-1"}' -H "Content-Type:application/json" > /reports/J.3.4_deploy.json || true
```

### J.3.5 — Vendor Portal
**Branch:** `prod-feature/J.3.5-vendor-portal`  
**Files**
```
services/vendor-portal/main.py
services/vendor-portal/analytics.py
services/vendor-portal/publisher.py
services/vendor-portal/tests/test_portal.py
reports/J.3.5_vendor_portal.md
```
**Endpoints**
- `GET /vendor/dashboard/{vendor_id}` → Analytics dashboard
- `POST /vendor/packages/upload` → Package publishing
- `GET /vendor/revenue/{vendor_id}` → Revenue reports
**Behavior**
- Package upload and validation pipeline
- Download analytics and user feedback
- Revenue tracking and payout management
- A/B testing for package descriptions
**Verification**
```
pytest -q services/vendor-portal/tests/test_portal.py > /reports/logs/J.3.5.log 2>&1 || true
curl -s http://localhost:9305/vendor/dashboard/vendor-1 > /reports/J.3.5_dashboard.json || true
```

### J.3.6 — Marketplace UI
**Branch:** `prod-feature/J.3.6-marketplace-ui`  
**Files**
```
ui/marketplace/pages/index.tsx
ui/marketplace/components/PackageCard.tsx
ui/marketplace/components/SearchFilters.tsx
ui/marketplace/package.json
ui/marketplace/tailwind.config.js
reports/J.3.6_marketplace_ui.md
```
**Features**
- Package discovery with AI recommendations
- Advanced search and filtering
- User reviews and ratings
- One-click deployment integration
- Vendor profiles and analytics
**Verification**
```
cd ui/marketplace && npm install && npm run build > /reports/logs/J.3.6.log 2>&1 || true
curl -s http://localhost:3006/health > /reports/J.3.6_ui_health.json || true
```

---

## Precheck (agent-run)

```
mkdir -p reports/logs
python - <<'PY' > reports/J.3_precheck.json
import os,json
r={k:('SET' if os.getenv(k) else 'MISSING') for k in ['POSTGRES_DSN','VAULT_ADDR','MARKETPLACE_API_URL','PAYMENT_GATEWAY_URL']}
r['SIMULATION_MODE']=os.getenv('SIMULATION_MODE','true')
r['decision']='PROCEED' if r['POSTGRES_DSN']=='SET' else 'PROCEED_SIMULATION'
print(json.dumps(r,indent=2))
PY
```

Decision:
- `PROCEED_SIMULATION` if any critical missing
- `PROCEED` only if DB + payment gateway available

---

## Integration tests (end-to-end)

Create `tests/integration/test_J.3_end2end.py` to exercise:
- Package publishing workflow
- AI quality scoring pipeline
- Payment processing (mock)
- Package deployment
- Vendor analytics

```
pytest -q tests/integration/test_J.3_end2end.py > /reports/logs/J.3_end2end.log 2>&1 || true
```

---

## Verification & reporting

For each task produce `/reports/J.3.*.md` with:
- Branch name and commit SHA
- Precheck summary and `SIMULATION_MODE`
- Tests PASS/FAIL counts and excerpts
- Verification curl outputs
- Policy matrix (P1–P7) with PASS/BLOCKED flags
- Marketplace metrics (packages, revenue, deployments)
- Blockers and next steps

Agent must also produce `/reports/PhaseJ.3_Snapshot.json` via `scripts/generate_phase_snapshot.py`.

---

## Deliverables

- All `services/*` implemented with tests and `config.example.yaml`
- `ui/marketplace/*` with ATOM theme integration
- `/docs/policies/marketplace_policy.md`
- `/reports/J.3.*.md` + logs
- `tests/integration/test_J.3_end2end.py`
- `/reports/PhaseJ.3_Snapshot.json`

---

## Agent execution rules

1. Run precheck. If decision `BLOCK` create `/reports/PhaseJ.3_precheck_block.txt` and stop.
2. For each J.3.x:
   - `git checkout -b prod-feature/J.3.x-<short>`
   - Create files listed
   - Run unit tests and save logs `/reports/logs/J.3.x.log`
   - Start service locally (uvicorn) if needed for verification
   - Run verification curl commands and save outputs under `/reports/`
   - Commit locally with message `feat(J.3.x): <short> implemented (agent)`
   - Do not push or create PRs automatically.
3. After all tasks run integration tests and produce snapshot.
4. Always redact secrets. Never log secrets or raw PII.
5. If production activation desired, require human review for payment gateway integration.

---

## Embedded agent prompt

```
You are the ATOM coding agent. Execute Phase J.3 per /docs/Phase_J.3_Marketplace_Agent.md. Run precheck. If critical infra missing set SIMULATION_MODE=true and annotate reports. Implement tasks J.3.1→J.3.6, create marketplace services, AI scorer, payment engine, and UI. Commit locally per task. Do not push or create PRs. Never log secrets. Enforce P1–P7. Start now and complete autonomously.
```

---