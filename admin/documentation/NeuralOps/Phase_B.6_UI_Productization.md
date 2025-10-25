# `/docs/Phase_B.6_UI_Productization.md` — Agent-ready

**Goal:** Build NeuralOps UI and productization assets. Provide incident dashboard, approval UX, playbook catalog, onboarding flows (BYOC), and basic billing/tenant views.
**Branch:** `prod-feature/B.6-ui`
**Duration:** 2–4 days (agent-run)

---

## 1 — Scope (minimal MVP)

Front-end stack: Next.js (React). Single repo single-file deployable app with API proxies to backend services.

User roles:

* `viewer` — view incidents, logs.
* `operator` — run dry-runs, request approval.
* `org-admin` — approve and execute, manage tenants.

Pages:

* `/`  Landing / product intro
* `/dashboard`  Incident list + summary
* `/incidents/[id]`  Incident detail, timeline, logs, runbook, approve/execute buttons
* `/playbooks`  Catalog + view, dry-run button
* `/onboard`  BYOC cluster onboarding wizard
* `/settings`  Tenant settings, API keys, billing placeholder

Mobile responsive, light theme (white background).

---

## 2 — Deliverables / Files

```
ui/neuralops/
  ├─ package.json
  ├─ next.config.js
  ├─ pages/
  │   ├─ index.jsx
  │   ├─ dashboard.jsx
  │   ├─ incidents/[id].jsx
  │   ├─ playbooks.jsx
  │   ├─ onboard.jsx
  │   └─ settings.jsx
  ├─ components/
  │   ├─ Header.jsx
  │   ├─ IncidentCard.jsx
  │   ├─ PlaybookCard.jsx
  │   ├─ ApproveModal.jsx
  │   └─ Toast.jsx
  ├─ styles/globals.css
  ├─ api-proxy/
  │   └─ server.js   # simple proxy for AUTH and CORS with env config
  ├─ tests/
  │   └─ ui_smoke.test.js
  ├─ infra/helm/ui/    # minimal chart or k8s manifest
  └─ docs/ui_api.md
```

Also add docs/policies/ui_approval_flow.md and docs/policies/ui_security.md.

---

## 3 — UX Behavior & Flows

### Incident list (/dashboard)

* shows incident card with: id, created_at, severity, status, recommended playbook(s), last_update.
* filters: status, severity, time range, tenant
* search: free-text across id and playbook

### Incident detail (/incidents/[id])

* timeline: suggest → dry-run → approval → execute → result
* logs viewer (tail, download)
* playbook preview with node list
* buttons:

  * "Request Dry-Run" → calls Orchestrator `/orchestrations/{id}/dry-run`
  * "Request Approval" → opens ApproveModal (requires operator JWT)
  * "Execute" → visible/enabled only after approval and org-admin JWT
* show audit hash and link to S3 audit file

### Playbook catalog (/playbooks)

* list with tags, safety.mode, success_rate metric from recommender
* "Dry-Run" button (simulated)
* "Add to Watchlist" for auto-suggest training

### Onboard (/onboard)

* Upload kubeconfig or paste cluster token
* Run quick connectivity checks (prometheus up, kubectl apply dry-run)
* Register to NeuralOps via orchestrator `/register` endpoint

### Settings

* Tenant config: RLS test, cosign public key upload (view-only)
* Billing placeholder (monthly usage metric tile)

---

## 4 — APIs used (backends must exist)

* Recommender: `GET http://localhost:8003/recommend?signal_id={id}`
* Orchestrator: `POST http://localhost:8004/orchestrate`, `/approve`, `/execute`, `/incidents/{id}`
* Registry: `POST http://localhost:8000/workflows/{id}/dry-run`
* Runtime-agent: `POST http://localhost:8001/execute` (shown in UI as status only)
* Insight Engine: `GET http://localhost:8002/signals/{id}` (for charts)
* Auth: Verify JWT locally or via auth service (envible `AUTH_PUBLIC_KEY`)
* S3 Audit link pattern from config

`ui/api-proxy/server.js` will proxy requests and inject JWT from local dev env.

---

## 5 — Security & Policies (must be enforced in UI / agent)

* All action buttons call backend which enforces policy. UI must not be the gatekeeper.
* UI must require appropriate JWT scopes:

  * `approve:org` for approve
  * `execute:playbook` for execute
* Do not display sensitive secret values.
* CSRF protection via SameSite cookies if using cookie auth.
* HTTPS only in production.

Add `docs/policies/ui_approval_flow.md` with:

* minimum approval payload: `{ incident_id, approver_id, justification, timestamp }`
* retention and audit linkage (S3 path + SHA256)

---

## 6 — Tests & Verification

* Unit/Snapshot tests for components.
* End-to-end smoke test (puppeteer/playwright minimal):

  * load `/dashboard` → validate incident card present
  * open first incident → request dry-run → expect dry-run response
  * open approve modal → simulate JWT with org-admin role → click approve → expect 200
  * (if orchestrator unavailable mark BLOCKED but simulate)

Commands:

```bash
cd ui/neuralops
npm ci
npm run test
npm run build
npm run start   # for smoke run
# smoke test
node tests/ui_smoke.test.js
```

Save artifacts:

* `/reports/B.6_ui.md`
* `/reports/logs/B.6_ui.log`
* Screenshot folder `/reports/ui_screenshots/`

---

## 7 — Acceptance Criteria

* UI builds (`npm run build`) → PASS
* Smoke test passes or fails only due to blocked infra (record BLOCKED)
* Approve flow triggers backend calls and records audit entry
* Playbook preview shows node list and `safety.mode`
* Onboard flow registers cluster (or simulated success) and writes status

---



---

## 9 — Minimal UI design notes (visual tone)

* White background, soft gradients on cards.
* Modern sans-serif, roomy spacing.
* Clean iconography for stages (circle icons colored by status).
* Primary CTA color: indigo (#4F46E5). Accent: cyan (#06B6D4).
* Simple logo (ATOM nucleus) top-left.

---

## 10 — Post-success tasks

* Export screen recordings or screenshots to `/reports/ui_screenshots/`.
* Add UI to Helm chart infra/helm/ui for staging.
* Document deploy steps in `docs/ui_api.md`.

---

## 11 — Output (files agent must create)

* `/docs/Phase_B.6_UI_Productization.md` (this file saved)
* `ui/neuralops/*` per folder list
* `/reports/B.6_ui.md` and `/reports/logs/B.6_ui.log`
* PR to `prod-feature/B.6-ui`

---


