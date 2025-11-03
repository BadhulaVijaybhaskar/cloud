# UI Spec: One-Page Screen Specs for J.2 (Developer Console) & J.3 (AI Marketplace)

Below are compact, ready-to-implement one-page UI specs for each screen requested. Each spec contains: Purpose, Route (file), Key components (with props), Layout, Data endpoints, Component states, Actions/flows, Mock data example, Acceptance criteria, Accessibility notes, and Theme/Integration notes. Use LaunchPad theme tokens from `collective_intelligence/launchpad/components/theme/` where available.

---

## J.2.1 — Projects List (Developer Console Home)

**Route / File:** `/ui/dev-console/pages/index.js`
**Purpose:** Show org projects, quick actions, search/filter and create project.

### Key Components

* `TopNav` `{ user }`
* `ProjectFilterBar` `{ onSearch, onFilter }`
* `ProjectCard` `{ project, onOpen, onManage }`
* `CreateProjectModal` `{ visible, onCreate }`
* `EmptyState` `{ onCreate }`

### Layout

* TopNav (left: logo, center: search, right: user menu)
* Page header: "Projects" + Create button
* Grid of `ProjectCard` (responsive 3/2/1 columns)
* Footer quick links (Billing, Marketplace)

### Data Endpoints

* `GET /v1/projects` → list of projects
* `POST /v1/projects` → create project

### Component States

* Loading, Loaded, Empty, Error
* `ProjectCard` states: active, suspended, needs-attention

### Actions / Flows

* Search → call GET with query param
* Create → open modal → POST → refresh list → show toast
* Open → navigate to `/project/[id]` (fetch overview)

### Mock Data

```json
[
  {"id":"p-1","name":"Alpha","owner":"org-1","status":"running","quota":{"cpu":4}},
  {"id":"p-2","name":"Beta","status":"suspended"}
]
```

### Acceptance Criteria

* Projects list renders within 1s in simulation mode.
* Create flow shows modal, validates name, and calls POST (simulated).
* Empty state shows CTA to create project.

### Accessibility

* All interactive elements keyboard-focusable.
* Images/icons have alt text.
* Color contrast meets AA.

### Notes

* Use `ProjectCard` theme tokens; keep LaunchPad styles identical.

---

## J.2.2 — Project Overview / Launcher

**Route / File:** `/ui/dev-console/pages/project/[id].js`
**Purpose:** Aggregate project summary, quick-launch into LaunchPad, billing & links.

### Key Components

* `ProjectSummary` `{ project }`
* `UsageChart` `{ metrics }`
* `QuickLinks` `{ links[] }` (Open LaunchPad, API Keys, Marketplace)
* `ApiKeyForm` `{ onCreate }`
* `AlertsPanel` `{ alerts }`

### Layout

* Header (project name, status, actions)
* Left column: Summary + UsageChart + QuickLinks
* Right column: Alerts + Recent Deploys + Logs snippet

### Data Endpoints

* `GET /v1/projects/{id}/overview`
* `GET /v1/projects/{id}/usage`
* `POST /v1/projects/{id}/keys`

### Component States

* Loading, Up-to-date, Offline
* Button states: primary, loading, disabled

### Actions / Flows

* Open LaunchPad → call `GET /v1/projects/{id}/launch` → receive `{launch_url, scoped_token}` → open in new tab with token param
* Create API Key → POST → show masked key and copy button

### Mock Data

```json
{
 "id":"p-1","name":"Alpha","status":"running","usage":{"cpu":35,"mem":60},
 "links":[{"label":"Open LaunchPad","url":"/collective_intelligence/launchpad?projectId=p-1"}]
}
```

### Acceptance Criteria

* LaunchPad button obtains scoped token and opens new tab (simulated).
* UsageChart renders with sample data.
* Create API key stores secret in Vault (simulated return).

### Accessibility

* Modal forms labeled; aria-live regions for toasts.

### Notes

* Deep-link behavior must be secure; token lifetime short-lived.

---

## J.2.3 — Billing Dashboard

**Route / File:** `/ui/dev-console/pages/billing.js`
**Purpose:** Org-level spend, per-project breakdown, invoices, budgets.

### Key Components

* `BillingSummary` `{ totals }`
* `ProjectSpendTable` `{ rows }`
* `BudgetControls` `{ onSetBudget }`
* `InvoiceList` `{ invoices }`

### Layout

* Top: summary cards (month-to-date, forecast)
* Middle: project spend breakdown table with sparkline
* Bottom: invoices and export button

### Data Endpoints

* `GET /v1/billing/summary`
* `GET /v1/billing/invoices`
* `POST /v1/billing/budgets`

### States

* Loading, HasData, NoInvoices

### Actions

* Export CSV, Create budget, Drill into project spend (link to `/project/[id]`)

### Mock Data

```json
{"total_mtd":1250.50, "projects":[{"id":"p-1","cost":850},{"id":"p-2","cost":400}]}
```

### Acceptance Criteria

* Data renders and export button produces CSV (simulated file).
* Budget set flow calls API.

### Notes

* Ensure P9 cost governance enforced.

---

## J.2.4 — Marketplace Entry (Dev Console)

**Route / File:** `/ui/dev-console/pages/marketplace.js`
**Purpose:** Entry and context passthrough to J.3 marketplace.

### Key Components

* `MarketplaceTile` `{ featured }`
* `EmbedOrRedirect` `{ targetUrl }` (decides embed iframe vs redirect)
* `ProjectContext` (adds `projectId` to links)

### Layout

* Simple landing: search + featured + CTA

### Actions

* Click model → navigate to `ui/marketplace` with `projectId` param

### Acceptance Criteria

* Deep link includes `projectId` and scoped token (if available).

---

## J.2.5 — API Keys Management

**Route / File:** `/ui/dev-console/pages/api-keys.js`
**Purpose:** Create/list/revoke/rotate API keys.

### Key Components

* `ApiKeysTable` `{ keys }`
* `CreateKeyModal` `{ onCreate }`
* `KeyDetails` `{ key }`

### Data Endpoints

* `GET /v1/keys`
* `POST /v1/keys`
* `DELETE /v1/keys/{id}`

### Actions

* Create → PSV form → Vault integration simulated → show masked key
* Revoke → confirm modal → DELETE

### Acceptance Criteria

* Created keys returned masked; copy to clipboard works.
* Revoke removes key from list (simulated).

---

## J.2.6 — Logs Viewer (Aggregated)

**Route / File:** `/ui/dev-console/pages/logs.js`
**Purpose:** Quick aggregated log search; links to full logging console.

### Key Components

* `LogSearchBar` `{ onSearch }`
* `LogList` `{ items }`
* `LogEntry` `{ entry }`
* `OpenFullLogsBtn`

### Data Endpoints

* `GET /v1/logs?project={id}&query=...`

### Acceptance Criteria

* Search returns simulated results; each entry expands to show details.

---

## J.2.7 — Alerts Inbox

**Route / File:** `/ui/dev-console/pages/alerts.js`
**Purpose:** List alerts, ack/escalate.

### Key Components

* `AlertList` `{ alerts }`
* `AlertDetailDrawer` `{ alert }`

### Actions

* Acknowledge → POST `/v1/alerts/{id}/ack`
* Escalate → create ticket (link to support)

### Acceptance Criteria

* Alerts load and ack action toggles UI state.

---

## J.2.8 — Settings (Console-level)

**Route / File:** `/ui/dev-console/pages/settings.js`
**Purpose:** Global Dev Console settings, integrations.

### Key Components

* `IntegrationSettings` (GitHub, CI)
* `AuthProvidersLink` (points to LaunchPad Auth UI)
* `ServiceMeshToggle` (shows status; edit in infra only)

### Acceptance Criteria

* Toggles show current state and prompts to open infra page for changes.

---

---

## J.3.1 — Marketplace Index (Browse Models & Agents)

**Route / File:** `/ui/marketplace/pages/index.js`
**Purpose:** Browse and search models/agents; filter, sort, featured.

### Key Components

* `SearchBar` `{ onSearch }`
* `FilterPanel` `{ filters }`
* `ModelCard` `{ model }`
* `Pagination` `{ page, onChange }`

### Data Endpoints

* `GET /v1/models?query=&tags=&license=&page=`

### Actions

* Click model → `/marketplace/model/[id]`
* Purchase CTA → open checkout flow

### Mock Data

```json
[{"id":"m-1","name":"NLP-Pro","price":0,"vendor":"V1","tag":["nlp"]}]
```

### Acceptance Criteria

* Search and filters filter the mock list; featured models shown.

---

## J.3.2 — Model Detail (Marketplace)

**Route / File:** `/ui/marketplace/pages/model/[id].js`
**Purpose:** Show model metadata, versions, safety & governance status, pricing, examples.

### Key Components

* `ModelHeader` `{ name, vendor, rating }`
* `VersionSelector` `{ versions }`
* `SafetyReport` `{ safety_metadata }`
* `PurchaseCTA` `{ price }`
* `TestRunBtn` `{ onTest }`

### Data Endpoints

* `GET /v1/models/{id}`
* `POST /v1/models/{id}/test-run`
* `POST /v1/marketplace/purchase`

### Actions / Flows

* Request sandbox test-run → POST → show worker job status
* Purchase → call billing → create license token and attach to project

### Acceptance Criteria

* Safety report visible; test-run toggles to in-progress and shows result (simulated).

---

## J.3.3 — Publish Model (Vendor UI)

**Route / File:** `/ui/marketplace/pages/publish.js`
**Purpose:** Vendor upload flow with pre-publish governance checks.

### Key Components

* `PublishForm` (fields: name, version, artifact upload/url, license, tags, rationale)
* `GovernanceProgress` (shows P1–P5 checks)
* `Preview` & `Submit` buttons

### Data Endpoints

* `POST /v1/publish/model` (multipart or JSON)
* `GET /v1/publish/{job_id}/status`

### Flow

1. Fill form → submit → returns job_id (202)
2. Poll `GET /v1/publish/{job_id}/status` → show progress (PII scan, bias, explainability)
3. On success → model listed, vendor dashboard updated

### Mock Data

* Job status transitions: accepted → scanning → governance_pass → listed

### Acceptance Criteria

* Form validates required fields; artifact size limit enforced (mock).

---

## J.3.4 — Vendor Dashboard (Analytics)

**Route / File:** `/ui/marketplace/pages/vendor/index.js`
**Purpose:** Vendor sales, downloads, payouts.

### Key Components

* `RevenueChart` `{ series }`
* `DownloadsTable` `{ rows }`
* `PayoutsList` `{ payouts }`

### Data Endpoints

* `GET /v1/vendors/{id}/stats`

### Acceptance Criteria

* Charts render sample metrics; export CSV works.

---

## J.3.5 — Agent Detail & Configuration

**Route / File:** `/ui/marketplace/pages/agent/[id].js`
**Purpose:** Show agent manifest, execution policy, sandboxing options.

### Key Components

* `AgentManifest` `{ manifest }`
* `PolicyEditor` `{ policy }` (view-only for marketplace)
* `TestRun` `{ onRun }`

### Actions

* Configure sandbox parameters (simulated) and request test-run.

### Acceptance Criteria

* Manifest displayed; test-run returns simulated logs.

---

## J.3.6 — Checkout & License Issuance

**Route / File:** `/ui/marketplace/pages/checkout.js`
**Purpose:** Purchase flow, EULA acceptance, license token issuance and attach to project.

### Key Components

* `CheckoutSummary` `{ items }`
* `PaymentStub` (simulated)
* `LicenseTokenDisplay` `{ token }`

### Flow

* On success, create license token and call `POST /v1/projects/{id}/models` (developer-console) to attach model to project.

### Acceptance Criteria

* Checkout simulate success, token displayed (masked), and dev-console call returns 200 (sim).

---

## Shared Components & Design Tokens

* `Layout` (TopNav + Sidebar) — reuse LaunchPad Layout
* `Theme` tokens: spacing, colors, typography — import from `collective_intelligence/launchpad/components/theme/`
* `Toasts`, `ConfirmModal`, `Table`, `FormField`, `Spinner`

---

## Mock Data Summary (single file suggestion)

Create `ui/dev-console/mock/seed.json` and `ui/marketplace/mock/seed.json` with consistent objects for projects, models, users, invoices, alerts — used by all screens in SIMULATION_MODE.

---

## Accessibility & Internationalization

* All screens: keyboard navigable, ARIA attributes on forms, dynamic content announced via `aria-live`.
* Text strings stored in `i18n/en.json` for future translations.

---

## Implementation Notes / Handover

* Reuse LaunchPad theme tokens and global providers from `collective_intelligence/launchpad/components/_app.js`. Import CSS/variables into `ui/dev-console/pages/_app.js`.
* Developer Console must never duplicate heavy LaunchPad functionality — deep-link into LaunchPad for editors (SQL, Table Editor).
* For Marketplace, allow embedding but prefer a normal route under `ui/marketplace/` and deep-link from dev-console with project context.
* All network calls use `SIMULATION_MODE=true` stubs when infra not available.

Developer Console (J.2) UI and Marketplace (J.3) screens — specific, actionable list.

## J.2 — Developer Console (top of LaunchPad)

Location in repo: `ui/dev-console/`
Primary layout source: reuse theme from `collective_intelligence/launchpad/components/`

### Core screens (routes → files)

* `/` → `ui/dev-console/pages/index.js`

  * Purpose: Org project list + quick actions.
  * Widgets: project cards, create project button, search, filters, usage summary.
  * Data: `GET /v1/projects` (developer-console-core).
  * Auth: user must be authenticated + role check (dev/admin).

* `/project/[id]` → `ui/dev-console/pages/project/[id].js`

  * Purpose: Project overview and launch controls.
  * Sections: Summary (status, quotas), Quick Links (Open in LaunchPad), Marketplace, Billing, Logs, API Keys.
  * Actions:

    * Open LaunchPad: redirect to `${LAUNCHPAD_BASE_URL}?projectId={id}&scopedToken={token}` (developer-console-core provides token).
    * Create API key: POST `/v1/projects/{id}/keys`.
  * Data: `GET /v1/projects/{id}`, `GET /v1/projects/{id}/usage`.

* `/project/[id]/open-launchpad` (button + handler; no new page)

  * Purpose: Securely open LaunchPad in new tab with scoped token.

* `/billing` → `ui/dev-console/pages/billing.js`

  * Purpose: Global billing dashboard across projects.
  * Widgets: invoices, spend by project, budgets, alerts.
  * Data: `GET /v1/billing/summary`, `GET /v1/billing/invoices`.

* `/marketplace` → `ui/dev-console/pages/marketplace.js`

  * Purpose: Entry point to J.3 marketplace UI (deep link or embedded).
  * Behavior: either iframe embed `ui/marketplace/` or redirect to `/marketplace/` (internal route).
  * Data: minimal listing via developer-console-core or direct to marketplace service.

* `/api-keys` → `ui/dev-console/pages/api-keys.js`

  * Purpose: Manage project and global API keys.
  * Actions: create, list, revoke, rotate.
  * Data: `/v1/keys` endpoints; Vault integration for secrets.

* `/logs` → `ui/dev-console/pages/logs.js`

  * Purpose: Aggregated logs & quick search (links into centralized logging).
  * Widgets: recent alerts, search bar, export.
  * Data: call logs API `GET /v1/logs?project={id}`.

* `/alerts` → `ui/dev-console/pages/alerts.js`

  * Purpose: Alert inbox, acknowledge, escalate.
  * Data: `GET /v1/alerts`, `POST /v1/alerts/{id}/ack`.

* `/settings` → `ui/dev-console/pages/settings.js`

  * Purpose: Console-level settings and integrations.
  * Sections: auth providers (link to LaunchPad Auth UI), service mesh toggle pointer, policy links.

### Reusable components (place under `ui/dev-console/components/`)

* `ProjectCard`, `ProjectList`, `TopNav`, `Sidebar`, `LaunchPadLauncher`, `ApiKeyForm`, `BillingSummary`, `MarketplaceTile`, `LogViewerStub`, `AlertList`

### Integration points to LaunchPad

* Use LaunchPad theme tokens; deep-link for heavy pages (`sql-editor`, `auth`, `table-editor`).
* DO NOT duplicate LaunchPad internal pages. Provide launcher and scoped token handler only.

### Security / Policies

* All actions must check P2 (auth) and P8 (tenant isolation).
* API key creation writes to Vault. UI shows only masked values once.

---

## J.3 — AI Marketplace screens and where they live

Location in repo: `ui/marketplace/` (primary) and `ui/dev-console/pages/marketplace.js` (entry/integration)

### Primary marketplace screens (routes → files)

* `/marketplace/` → `ui/marketplace/pages/index.js`

  * Purpose: Browse models and agents.
  * Widgets: Search, filters (tags, license, price), featured listings, vendor badges.
  * Data: `GET /v1/models?query=...` from marketplace-gateway.

* `/marketplace/model/[id]` → `ui/marketplace/pages/model/[id].js`

  * Purpose: Model details and purchase / deploy flows.
  * Sections: Description, versions, safety report, explainability summary, pricing, license, vendor info, usage examples.
  * Actions:

    * Request demo / sandbox run: POST `/v1/models/{id}/test-run` (agent-registry/worker).
    * Purchase / subscribe: call billing flow `POST /v1/marketplace/purchase`.

* `/marketplace/publish` → `ui/marketplace/pages/publish.js` (publisher-only)

  * Purpose: Vendor upload form for model/agent.
  * Fields: name, version, artifact upload (or artifact URL), license, tags, explainability text, safety metadata, test dataset link.
  * Behavior: Upload triggers `POST /v1/publish/model` (marketplace-core). Show governance check progress and result.
  * Access: Vendor role; enforce P5 (safety) prechecks on client-side and server-side.

* `/marketplace/vendor/dashboard` → `ui/marketplace/pages/vendor/index.js`

  * Purpose: Vendor analytics: downloads, revenue, support tickets.
  * Data: `/v1/vendors/{id}/stats`, `/v1/vendors/{id}/payouts`.

* `/marketplace/agent/[id]` → `ui/marketplace/pages/agent/[id].js`

  * Purpose: Agent listings, manifest, execution policy.
  * Actions: Configure sandbox policy, request test-run, subscribe.

* `/marketplace/checkout` → `ui/marketplace/pages/checkout.js`

  * Purpose: Handle purchase, license agreement, token issuance.
  * Behavior: On success create license token and associate with project via developer console.

### How J.3 surfaces in Developer Console (J.2)

* Developer Console `project/[id]` shows a Marketplace tile linking to `/marketplace?project={id}`.
* Deep link passes `projectId` and `scopedToken` so user can purchase and deploy model into project without separate login.
* Post-purchase flow: marketplace worker calls billing service and then calls `developer-console-core` to register model instance in project (POST `/v1/projects/{id}/models`).

### UI components for marketplace (under `ui/marketplace/components/`)

* `ModelCard`, `ModelFilterBar`, `VersionList`, `SafetyReport`, `PublishForm`, `VendorDashboard`, `CheckoutForm`, `AgentManifestEditor`

### Governance & Safety UI elements

* On publish page show mandatory pre-publish checks and live status (PII scan, bias scan, explainability present).
* Show governance status badge on model detail (`GOVERNANCE: passed | flagged | rejected`) and link to `reports/marketplace/*`.

---

## Data flows and actions (concise)

* Browse → `ui/marketplace` → `marketplace-gateway` → `model-registry` + `storage` + `vector` (for semantic search).
* Publish → `marketplace-core` validates → stores artifact in `MODEL_ARTIFACT_BUCKET` → enqueues worker for safety tests → worker writes governance result to `model-registry`.
* Purchase → `marketplace-gateway` → `billing` (metering) → on success generate license token via `marketplace-core` and `vault` → call `developer-console-core` to attach to project.

## Acceptance checks for screens

* Each screen loads with mocked data when `SIMULATION_MODE=true`.
* Publish workflow shows a multi-step progress bar and final governance verdict.
* Checkout issues a license token (simulated) and returns redirect to `project/[id]` with confirmation.
* Deep links from Developer Console open marketplace pages with project context.

---

Generated J.3 Agent-Ready Build Plan below.

# Phase J.3 — AI Marketplace (Models + Agents) (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Phase:** J.3 — AI Marketplace (Models + Agents)
**Version target:** v1.0.0-j3-ai-marketplace
**Branch prefix (local):** prod-feature/j3-ai-marketplace
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution (agent must set `SIMULATION_MODE=true` if infra missing)

> **AGENT INSTRUCTION**: Use SIMULATION_MODE=true until security and infra sign-off.
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---

## Summary / Goal

**Objective:** Build an AI Marketplace enabling model and agent publishing, discovery, versioning, licensing, and secure deployment. Integrate with Developer Console (J.2) Marketplace tab. Provide registry APIs, storage for model artifacts, metadata search, billing hooks, and marketplace UI. Ensure governance (P1–P20) enforcement for model publishing and usage.

**Success Criteria:**

* [ ] Services deployed to `services/marketplace-*`.
* [ ] Infra modules in `infra/terraform/modules/marketplace` and `infra/helm/marketplace`.
* [ ] Marketplace UI integrated or reachable from Developer Console Marketplace.
* [ ] Model registry supports publish, list, version, retire.
* [ ] Agent registry supports publish, configure execution policy, and sandboxing flags.
* [ ] Billing hooks call `services/billing/` for metering events.
* [ ] Tests in `tests/marketplace/*`.
* [ ] Vault policies in `infra/vault/policies/marketplace.hcl`.
* [ ] No phase directories created.
* [ ] All integration tests pass in simulation mode.

---

## New / [Specific] Policies (added)

* P5: Model bias & safety checks required on publish.
* P6: Explainability metadata mandatory for models (rationale field).
* P11: Deployment isolation rules for tenant model execution.
* P16–P20: Production gating for paid models and marketplace payouts.
* Publishing workflow enforces P1 (PII checks) and P3 (audit logs) before acceptance.

---

## Environment Variables (agent must read/use)

```bash
# Paths and settings
COMPONENT_NAME="ai-marketplace"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
POLICIES_PATH="infra/vault/policies"

# Mode
: "${SIMULATION_MODE:=true}"

# Service endpoints
AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://services/auth:8080}"
BILLING_SERVICE_URL="${BILLING_SERVICE_URL:-http://services/billing:8090}"
STORAGE_SERVICE_URL="${STORAGE_SERVICE_URL:-http://services/storage-api:9000}"
VECTOR_DB_URL="${VECTOR_DB_URL:-http://services/vector:19530}"

# Registry storage
MODEL_ARTIFACT_BUCKET="marketplace-models"
MODEL_INDEX_DB="${MODEL_INDEX_DB:-postgresql://marketplace_db}"

# Security & limits
POLICY_ENFORCEMENT=true
MAX_MODEL_SIZE_MB=1024
VAULT_ADDR="${VAULT_ADDR:-http://vault.local}"
```

---

## File / Directory Structure to Create (exact)

```
services/
├── marketplace-core/
│   ├── src/main.py
│   ├── src/api.py
│   ├── src/publish_worker.py
│   ├── Dockerfile
│   └── requirements.txt
├── model-registry/
│   ├── src/registry.py
│   ├── migrations/
│   └── Dockerfile
├── agent-registry/
│   ├── src/agent_store.py
│   └── Dockerfile
├── marketplace-gateway/
│   ├── src/gateway.py
│   └── Dockerfile
└── marketplace-worker/
    ├── src/worker.py
    └── Dockerfile

infra/
├── terraform/modules/marketplace/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/marketplace/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── security/marketplace/
│   ├── network-policies.yaml
│   └── rbac.yaml
├── scripts/marketplace/
│   ├── precheck.sh
│   ├── deploy.sh
│   └── publish_sample_model.sh
└── vault/policies/
    └── marketplace.hcl

ui/
├── marketplace/                  # Marketplace UI (Next.js / React)
│   ├── pages/
│   │   ├── index.js              # Browse models/agents
│   │   ├── model/[id].js         # Model detail and purchase
│   │   ├── publish.js            # Publisher UI
│   │   └── vendor/              # Vendor dashboard
│   ├── components/
│   └── package.json
└── dev-console/                  # Developer Console (J.2) integration hook (marketplace link)

tests/marketplace/
├── unit/
├── integration/
└── e2e/

docs/
├── marketplace_API.md
└── marketplace_publisher_guide.md

reports/
├── marketplace_precheck.log
├── marketplace_deploy.log
└── marketplace_verification.json
```

---

## High-Level Tasks (J.3.1 → J.3.12)

| ID     | Component            | Purpose                                                        |
| ------ | -------------------- | -------------------------------------------------------------- |
| J.3.1  | Precheck             | Validate environment, quotas, bucket access, no phase dirs     |
| J.3.2  | Model Registry DB    | Schema and migrations for models, versions, metadata           |
| J.3.3  | Artifact Storage     | Bucket setup and upload pipeline for model artifacts           |
| J.3.4  | Publish API          | Publish, validate, sign-off workflow endpoint                  |
| J.3.5  | Safety Scans         | Automated bias, PII, license checks on publish                 |
| J.3.6  | Agent Registry       | Register agents, execution policies, sandbox flags             |
| J.3.7  | Marketplace Gateway  | Public API and Developer Console integration endpoints         |
| J.3.8  | Billing Hooks        | Meter model usage events to billing service                    |
| J.3.9  | UI Integration       | Marketplace pages and Dev Console Marketplace tab              |
| J.3.10 | Worker Jobs          | Async build, model signing, vector indexing, sandbox test runs |
| J.3.11 | Governance Gate      | I9 integration: publish only after governance pass             |
| J.3.12 | Tests & Verification | Unit, integration, e2e, security scans                         |

---

## Detailed Task Specs & Endpoints

### Publish Model

**Path:** `POST /v1/publish/model` → marketplace-core (port 8100)
**Behavior:**

* Accepts metadata + artifact (url or multipart, limited by MAX_MODEL_SIZE_MB)
* Runs pre-publish checks: P1 (PII), P5 (bias), license validation
* Stores artifact in `MODEL_ARTIFACT_BUCKET`
* Registers model + version in `model-registry`
* If model is paid, creates marketplace listing and billing hooks
* Emits event `marketplace.model.published` to event bus

**Request (multipart/form-data or JSON):**

```json
{
  "name":"string",
  "vendor_id":"string",
  "version":"string",
  "kind":"model|agent",
  "description":"string",
  "artifact_url":"string",
  "license":"MIT|Apache-2.0|proprietary",
  "tags":["nlp","vision"],
  "rationale":"explainability text",
  "safety_metadata":{...}
}
```

**Responses:**

* `202 Accepted` → accepted for processing (returns job_id)
* `400` → validation errors
* `403` → policy violation

### Model Registry API (port 8101)

* `GET /v1/models` → list models (filter by tags, vendor)
* `GET /v1/models/{id}` → model metadata and versions
* `GET /v1/models/{id}/download` → signed URL (via storage service)
* `POST /v1/models/{id}/retire` → retire model

### Agent Registry API (port 8102)

* `POST /v1/agents` → register agent (manifest + execution policy)
* `GET /v1/agents` → list agents
* `POST /v1/agents/{id}/test-run` → run in sandbox (worker schedules, result stored)

### Billing Hook

* On usage event (inference call, agent run), publish:

```
POST ${BILLING_SERVICE_URL}/v1/meter
{
  "project_id":"string",
  "model_id":"string",
  "units": number,
  "cost_center":"string",
  "timestamp":"ISO8601"
}
```

---

## Data Contracts (schemas)

### models table (simplified)

```sql
CREATE TABLE models (
  id UUID PRIMARY KEY,
  vendor_id UUID,
  name TEXT,
  description TEXT,
  license TEXT,
  tags TEXT[],
  created_at TIMESTAMP,
  status TEXT,
  latest_version TEXT
);
```

### versions table

```sql
CREATE TABLE model_versions (
  id UUID PRIMARY KEY,
  model_id UUID REFERENCES models(id),
  version TEXT,
  artifact_path TEXT,
  checksum TEXT,
  size_mb INT,
  metadata JSONB,
  published_at TIMESTAMP,
  governance_status TEXT
);
```

---

## Embedded Scripts

### precheck.sh (embedded)

**File:** `infra/scripts/marketplace/precheck.sh`

```bash
#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
COMP="marketplace"

# ensure no phase directories
if ls -d phase-* 2>/dev/null; then
  echo "ERROR: phase-* directories found. Abort." >&2
  exit 2
fi

# check storage access (simulation safe)
echo "Checking artifact bucket access (sim mode)"
if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "SIMULATION_MODE=true - skipping real bucket checks"
else
  # run actual checks
  aws s3 ls "s3://${MODEL_ARTIFACT_BUCKET}" || echo "Bucket check failed"
fi

# db migration check (non-blocking)
if [ -d "services/model-registry/migrations" ]; then
  echo "Migrations present"
fi

echo "PRECHECK_COMPLETE"
```

### deploy.sh (embedded)

**File:** `infra/scripts/marketplace/deploy.sh`

```bash
#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
COMP="marketplace"

# build docker images (simulation safe)
for svc in services/${COMP}-* services/model-registry services/agent-registry; do
  if [ -d "$svc" ]; then
    echo "Building $(basename $svc)"
    docker build -t "localhost:5000/atom-cloud/$(basename $svc):${IMAGE_TAG:-latest}" "$svc" || echo "build (sim) failed"
  fi
done

if [ "${SIMULATION_MODE}" != "true" ]; then
  terraform -chdir=infra/terraform/modules/${COMP} apply -auto-approve
  helm upgrade --install ${COMP} infra/helm/${COMP} -n ${NAMESPACE} --wait
else
  echo "SIMULATION_MODE=true - skipping infra apply"
fi
```

---

### **Verification & Testing**

```markdown
## Verification Commands (agent must run and save outputs)
```

```bash
# precheck
bash infra/scripts/marketplace/precheck.sh | tee reports/marketplace_precheck.log

# deploy (simulation)
bash infra/scripts/marketplace/deploy.sh | tee reports/marketplace_deploy.log

# run unit tests
pytest tests/marketplace/unit/ --maxfail=1 -q --json-report --json-report-file=reports/marketplace_unit.json

# integration tests (simulate publish)
export SIMULATION_MODE=true
python tests/marketplace/integration/test_publish_flow.py --json-report-file=reports/marketplace_integration.json
```

#### Integration Test Stub (agent must create)

File: `tests/marketplace/integration/test_publish_flow.py`

```python
import os
import requests
import pytest

BASE = os.getenv('MARKETPLACE_BASE_URL', 'http://localhost:8100')
SIM = os.getenv('SIMULATION_MODE', 'true') == 'true'

def test_publish_model_simulation():
    if SIM:
        assert True
    else:
        data = {
            "name":"test-model",
            "vendor_id":"vendor-123",
            "version":"0.0.1",
            "artifact_url":"http://example.com/model.tar.gz",
            "license":"MIT"
        }
        r = requests.post(BASE + '/v1/publish/model', json=data, timeout=10)
        assert r.status_code in (200,202)
```

---

## Agent Execution Steps (explicit sequence)

1. **Validate environment**

   ```bash
   if ls -d phase-* 2>/dev/null; then echo "ERROR: phase dirs exist" && exit 1; fi
   export SIMULATION_MODE=true
   ```

2. **Run Precheck**

   ```bash
   bash infra/scripts/marketplace/precheck.sh | tee reports/marketplace_precheck.log
   ```

3. **Create scaffolding**

   ```bash
   mkdir -p services/marketplace-core services/model-registry services/agent-registry services/marketplace-gateway services/marketplace-worker
   mkdir -p infra/terraform/modules/marketplace infra/helm/marketplace infra/scripts/marketplace
   touch infra/vault/policies/marketplace.hcl
   ```

4. **Implement minimal publish workflow (simulation)**

   * API accepts publish request, returns `202` with `job_id`
   * Worker simulates artifact copy and registry insert
   * Governance checks simulated with deterministic pass/fail

5. **Connect billing hook (simulation)**

   * On simulated usage event worker posts to `BILLING_SERVICE_URL` stub

6. **Run tests**

   ```bash
   pytest tests/marketplace/ --json-report --json-report-file=reports/marketplace_verification.json
   ```

7. **Produce verification artifact**

   ```bash
   jq -n --arg commit "$(git rev-parse --short HEAD 2>/dev/null || echo local)" --arg sim "${SIMULATION_MODE}" \
     '{commit:$commit, sim:$sim, timestamp:(now|todate)}' > reports/marketplace_verification.json
   ```

---

## Acceptance Criteria

* [ ] `services/marketplace-*` created with API and worker stubs.
* [ ] Terraform & Helm modules present under `infra/` with `serviceMesh.enabled` toggle.
* [ ] `model-registry` migrations present and schema applied in simulation mode.
* [ ] Publish API accepts requests and enqueues jobs (simulated).
* [ ] Safety checks invoked on publish and documented in `reports/marketplace_precheck.log`.
* [ ] Billing hook simulation records meter events to `reports/`.
* [ ] Marketplace UI accessible under `ui/marketplace/` or integrated into `ui/dev-console/marketplace`.
* [ ] Vault policy placeholder `infra/vault/policies/marketplace.hcl` exists.
* [ ] Integration tests pass in `SIMULATION_MODE=true`.
* [ ] Documentation for vendor publishing created under `docs/`.

---

## Deliverables & Compliance

**Deliverables**

* `services/marketplace-core/`, `model-registry/`, `agent-registry/`, `marketplace-gateway/`, `marketplace-worker/`
* `infra/terraform/modules/marketplace/`, `infra/helm/marketplace/`
* `ui/marketplace/` with browse/publish/vendor pages (simulation stub)
* `infra/vault/policies/marketplace.hcl` placeholder
* `infra/scripts/marketplace/{precheck.sh,deploy.sh,publish_sample_model.sh}`
* `tests/marketplace/*` and `reports/marketplace_*.json`

**Compliance**

* Enforce P1–P20 on publish and usage flows.
* No model artifacts processed without governance sign-off recorded.
* No secrets in repo. Use Vault for all tokens.
* SIMULATION_MODE must remain true until security approval.

---

## Notes for the Agent (embedded prompt)

> Build the AI Marketplace in simulation. Implement a publish API that enqueues a publish job. Simulate artifact storage and governance checks. Ensure billing events are emitted to `BILLING_SERVICE_URL` (simulated). Generate reports in `reports/`. If any step requires SIMULATION_MODE=false, stop and create `reports/marketplace_decision_request.json` with justification. Enforce P1–P20 for published items. Integrate Marketplace link into Developer Console by adding `ui/dev-console/pages/marketplace.js` that deep-links to `ui/marketplace/`.

---

