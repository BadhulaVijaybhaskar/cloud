# Naksha Cloud — Complete Project Specification (MVP)

**Format:** Markdown with embedded JSON blocks for machine parsing.
**Scope:** Supabase-like backend only. Managed Postgres, Auth, Storage (S3), Realtime, API (GraphQL/REST), Admin UI, TypeScript SDK, dev infra.
**Priority:** Build exact MVP flow: developer creates workspace → creates schema data → CRUD via API → storage upload → realtime events → admin console.

---

## 1 — Executive summary

Naksha Cloud MVP is a multi-tenant backend platform that provides:

* Managed Postgres with schema-per-tenant
* Auth (email/password + JWT) and workspace RBAC
* S3-compatible storage (MinIO) with presigned uploads
* GraphQL API (Hasura) + minimal REST endpoints for auth and storage
* Realtime (pg_notify → WebSocket) for subscriptions/events
* Admin UI (React) for tenants and system admins
* TypeScript SDK for quick integration

Deliverables: runnable `docker compose up --build`, DB migrations, admin UI, SDK, CI e2e test.

---

## 2 — Implementation constraints

* Language: TypeScript (Node 18+). Frontend: React + Tailwind.
* Containerization mandatory. Provide `Dockerfile` for each service.
* Use Hasura for GraphQL & RLS rules. Fallback: PostgREST + custom gateway if not available.
* Use Prisma for migrations and type-safe DB access for custom endpoints.
* LLM/AI features excluded. pgvector optional (flag `ENABLE_PGVECTOR=true`).
* No external paid services required for local dev.

---

## 3 — System components (short list)

```json
{
  "components": [
    {"name":"postgres","type":"db","image":"postgres:15","ports":[5432]},
    {"name":"hasura","type":"graphql","image":"hasura/graphql-engine"},
    {"name":"auth","type":"service","impl":"GoTrue or custom-express-jwt"},
    {"name":"minio","type":"object_store","image":"minio/minio"},
    {"name":"realtime","type":"service","impl":"node-ws-pgnotify"},
    {"name":"admin-ui","type":"frontend","impl":"react-next"},
    {"name":"sdk","type":"package","lang":"typescript"},
    {"name":"migrations","type":"prisma/sql","path":"backend/prisma"}
  ]
}
```

---

## 4 — Topology & ports

* Postgres: `5432`
* Hasura: `8080`
* Auth service: `9999` (REST)
* MinIO: `9000` (console `9001`)
* Realtime WS: `4000`
* Admin UI: `3000`
  Expose via `docker-compose.dev.yml`. All services in same docker network `naksha-net`.

---

## 5 — Multi-tenancy model

**Schema-per-tenant** for MVP.

* Each workspace = Postgres schema `ws_<uuid>`.
* Shared `public` schema contains `workspaces`, `users`, `billing`, `system_events`.
* Hasura metadata maps per-tenant GraphQL permissions by searching `request.headers['x-workspace-id']` and setting `search_path` in DB session.

---

## 6 — Data model (SQL + Prisma). Use these migrations.

### 6.1 Public schema SQL

```sql
-- public/001_create_public_tables.sql
CREATE TABLE public.users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE public.workspaces (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  owner_id uuid REFERENCES public.users(id),
  created_at timestamptz DEFAULT now()
);

CREATE TABLE public.workspace_members (
  workspace_id uuid REFERENCES public.workspaces(id),
  user_id uuid REFERENCES public.users(id),
  role text NOT NULL DEFAULT 'member',
  PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE public.artifact_store (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES public.workspaces(id),
  key text NOT NULL,
  url text NOT NULL,
  size_bytes bigint,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE public.events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid,
  project text,
  type text,
  payload jsonb,
  created_at timestamptz DEFAULT now()
);
```

### 6.2 Tenant schema example (create on workspace creation)

```sql
-- tenant template: create tables inside ws_<id>
CREATE TABLE projects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  created_by uuid,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(id),
  data jsonb,
  created_at timestamptz DEFAULT now()
);
```

If `ENABLE_PGVECTOR=true` include:

```sql
CREATE TABLE embeddings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid,
  text_chunk text,
  vector vector
);
```

---

## 7 — API contracts

### 7.1 Auth REST (Auth service)

OpenAPI minimal (machine JSON below).

```json
{
  "openapi":"3.0.0",
  "paths": {
    "/auth/register": {
      "post": {
        "requestBody":{"content":{"application/json":{"schema":{"type":"object","properties":{"email":{"type":"string"},"password":{"type":"string"}}}}}},
        "responses":{"200":{"description":"{token, user}"}}}
    },
    "/auth/login":{
      "post":{"requestBody":{"content":{"application/json":{"schema":{"type":"object","properties":{"email":{"type":"string"},"password":{"type":"string"}}}}}},"responses":{"200":{"description":"{token, user}"}}}
    },
    "/auth/me":{"get":{"security":[{"bearerAuth":[]}],"responses":{"200":{"description":"user"}}}}
  },
  "components":{"securitySchemes":{"bearerAuth":{"type":"http","scheme":"bearer"}}}
}
```

Tokens: JWT with `sub=user_id`, `exp=1h`, refresh token support optional.

### 7.2 GraphQL (Hasura)

Expose all tables in tenant schema using Hasura with RLS configured. Hasura session variables:

* `x-hasura-user-id`
* `x-hasura-role`
* `x-workspace-id` (used by permission rules)

GraphQL example operations:

* `mutation { insert_projects_one(object:{name:"Demo", description:"..."}) { id } }`
* `query { projects { id name } }`

### 7.3 Storage REST

* `POST /storage/presign` body `{workspace_id, key, content_type, size}` → returns `{upload_url, download_url, expires_at}` (PUT upload).
* `GET /storage/:workspace_id/list` → list artifacts (auth required).

### 7.4 Realtime WebSocket

Protocol:

* Client connects with `wss://host:4000?token=<JWT>&workspace=<id>`
* After connect send subscribe `{ "type":"subscribe", "channel":"projects:<projectId>" }`
* Server pushes messages `{ "type":"event", "channel":"projects:<projectId>", "payload":{...} }`
* Server relays `NOTIFY` from Postgres channel `projects_<projectId>`.

---

## 8 — Admin UI and Developer UI screens (detailed)

All screens include exact components, field names, and routes. Use design tokens from section later.

### 8.1 Routes map

```json
{
  "routes":[
    { "path":"/auth/login", "name":"Login" },
    { "path":"/launchpad", "name":"Launchpad" },
    { "path":"/projects", "name":"ProjectsList" },
    { "path":"/project/:id", "name":"ProjectDashboard" },
    { "path":"/storage", "name":"StorageBrowser" },
    { "path":"/admin/tenants", "name":"AdminTenants" }
  ]
}
```

### 8.2 Screen: Launchpad `/launchpad`

* Components:

  * `IdeaInput` textarea `id=idea_input`
  * `AnalyzeButton` triggers `POST /projects` with `{name, description}`
  * `RecentIdeas` list from local storage
* Expected behavior: on success navigate to `/project/:id`.

### 8.3 Screen: Projects list `/projects`

* Table columns: `Name`, `Created By`, `Last Updated`, `Status`, `Actions`
* Action: `Open` → `/project/:id`; `Upload artifact` opens `Storage modal`.

### 8.4 Screen: Project dashboard `/project/:id`

Tabs: Overview | Data | Realtime | Artifacts

* Overview: shows project meta, `Run Flow` button (calls Hasura RPC or custom endpoint to enqueue event)
* Data: raw table viewer listing `items` with `JSON` preview
* Realtime: WS connection component showing incoming events feed
* Artifacts: list artifacts, show `Download` and `Copy URL`

### 8.5 Admin UI `/admin/tenants`

* Tenant list with `workspace_id`, `name`, `owner_email`, `db_size`, `created_at`
* Actions: `Open schema`, `Suspend workspace`, `Run backup`
* Backup action: triggers DB dump script into `backups/` and updates `public.backups` table.

(Full screen wireframes are provided as JSON components below.)

---

## 9 — UI component spec (JSON) — copyable

```json
{
  "components":[
    {"name":"Nav","props":["items","active"]},
    {"name":"ProjectTable","columns":["name","owner","updated_at","status","actions"]},
    {"name":"IdeaInput","props":["value","onSubmit"]},
    {"name":"ArtifactList","props":["artifacts"], "actions":["download","delete","copy_url"]},
    {"name":"RealtimeFeed","props":["channel"], "events":["event_received"]}
  ]
}
```

---

## 10 — Environment variables (`.env.example`)

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=naksha
POSTGRES_PASSWORD=naksha
POSTGRES_DB=naksha_system
HASURA_GRAPHQL_DATABASE_URL=postgres://naksha:naksha@postgres:5432/naksha_system
HASURA_GRAPHQL_ADMIN_SECRET=changeme
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
AUTH_JWT_SECRET=replace_with_strong_secret
ENABLE_PGVECTOR=false
NODE_ENV=development
```

---

## 11 — Docker compose template (machine JSON)

Use this block to generate `docker-compose.dev.yml`.

```json
{
  "version":"3.8",
  "services":{
    "postgres":{"image":"postgres:15","environment":{"POSTGRES_PASSWORD":"naksha","POSTGRES_USER":"naksha","POSTGRES_DB":"naksha_system"},"volumes":["pgdata:/var/lib/postgresql/data"],"ports":["5432:5432"]},
    "hasura":{"image":"hasura/graphql-engine:latest","environment":{"HASURA_GRAPHQL_DATABASE_URL":"${HASURA_GRAPHQL_DATABASE_URL}","HASURA_GRAPHQL_ADMIN_SECRET":"${HASURA_GRAPHQL_ADMIN_SECRET}"},"depends_on":["postgres"],"ports":["8080:8080"]},
    "minio":{"image":"minio/minio","command":"server /data --console-address :9001","environment":{"MINIO_ACCESS_KEY":"${MINIO_ACCESS_KEY}","MINIO_SECRET_KEY":"${MINIO_SECRET_KEY}"},"ports":["9000:9000","9001:9001"],"volumes":["miniodata:/data"],"depends_on":["postgres"]},
    "auth":{"build":"./services/auth","ports":["9999:9999"],"depends_on":["postgres"]},
    "realtime":{"build":"./services/realtime","ports":["4000:4000"],"depends_on":["postgres"]},
    "admin-ui":{"build":"./admin","ports":["3000:3000"],"depends_on":["hasura","auth"]}
  },
  "volumes":{"pgdata":{},"miniodata":{}}
}
```

---

## 12 — Hasura metadata & RLS rules (summary)

* For tenant isolation set Hasura session var `x-workspace-id`.
* Example permission for `projects`:

  * `select`: `{"workspace_id":{"_eq":"X-Hasura-Workspace-Id"}}`
* Set `search_path` per request by using Hasura `on_conflict` header or `db_role` function. For simplicity set `PGSSLMODE` and exec a SQL session `SET search_path = 'ws_<id>, public'` via a small proxy that sets it, or use Hasura actions that inject `x-hasura-default-role` mapping.

---

## 13 — SDK spec (TypeScript)

Provide `createClient(baseUrl: string, token?: string)` with methods:

* `from(table).select(where).insert(obj).update().delete()`
* `storage.presignUpload({workspace, key, contentType, size})`
* `auth.register(email,password)`, `auth.login(email,password)`, `auth.me()`
* `realtime.connect({token, workspace})` returns EventEmitter

Return types should be typed via Prisma generated types.

---

## 14 — Operational scripts (must exist)

* `infra/scripts/create_workspace.sh {workspace_name} {owner_email}`

  * Creates `public.workspaces` row, creates schema `ws_<id>` using template SQL, inserts default tables.
* `infra/scripts/backup_workspace.sh {workspace_id}` → dumps schema to `backups/ws_<id>_YYYYMMDD.sql`
* `infra/scripts/suspend_workspace.sh` → sets `workspaces.suspended=true` and disables tokens

---

## 15 — Acceptance tests (automated e2e)

Test flow (automation script or Playwright):

1. Register user → get JWT
2. Create workspace → ensure `public.workspaces` contains new row and schema exists
3. Use Hasura GraphQL to insert a project in tenant schema and read it back
4. Request presigned URL, PUT object to MinIO, ensure `public.artifact_store` row exists and download URL returns 200
5. Subscribe WebSocket to `projects:<projectId>` then `NOTIFY` Postgres channel and assert client receives message
6. Assert RLS prevents cross-workspace access by using different `x-workspace-id`

Tests must exit non-zero on failure and print logs.

---

## 16 — CI (GitHub Actions) minimal workflow

* Build Docker images, start `docker compose up -d`, run `infra/scripts/setup.sh` to seed admin, run e2e tests, tear down.

---

## 17 — Security & compliance

* JWT secrets rotate every 30 days.
* All sensitive env values must be set via secrets in CI.
* Admin UI requires `HASURA_GRAPHQL_ADMIN_SECRET` environment guard.
* Data retention and deletion policy: soft delete and GC older than 90 days for free tier.

---

## 18 — Monitoring & metrics

Expose `/metrics` on backend & realtime services for Prometheus:

* `naksha_api_requests_total`
* `naksha_db_connections`
* `naksha_minio_put_count`
* `naksha_realtime_connected_clients`

Set alerts for high queue length and failed deploys.

---

## 19 — Deployment notes (production outline)

* Replace single Postgres with managed Postgres cluster (Neon or RDS), run schema-per-tenant migration via Terraform.
* Move minio to S3.
* Run Hasura in HA mode with metadata persistence.
* Add Vault for secrets.
* Add billing meter service capturing `usage` table.

---

## 20 — Acceptance criteria (final)

* `docker compose up --build` completes and services reachable.
* `infra/scripts/create_workspace.sh Demo demo@naksha.test` creates schema and returns `workspace_id`.
* Following e2e script completes: create project, upload artifact, realtime event received.
* Admin UI lists workspace and artifacts.
* SDK runs sample script and interacts correctly.

---

## 21 — Wireframes & screens (machine JSON + brief)

Provide to the blackbox for UI generation.

### 21.1 Launchpad wireframe

```json
{
  "screen":"Launchpad",
  "route":"/launchpad",
  "layout":{"left":"IdeaInput","center":"Results","right":"RecentIdeas"},
  "components":[
    {"id":"IdeaInput","type":"textarea","placeholder":"Describe your product idea...","cta":"Analyze"},
    {"id":"Results","type":"card_list","items":["Research summary","Suggested project name","Start project button"]},
    {"id":"RecentIdeas","type":"list","items":["Idea 1","Idea 2"]}
  ]
}
```

### 21.2 Project Dashboard wireframe

```json
{
  "screen":"ProjectDashboard",
  "route":"/project/:id",
  "layout":{"top":"title_bar","left":"tabs","center":"tab_content","right":"events_timeline"},
  "tabs":["Overview","Data","Realtime","Artifacts"]
}
```

### 21.3 Admin Tenants

```json
{
  "screen":"AdminTenants",
  "route":"/admin/tenants",
  "tableColumns":["workspace_id","name","owner_email","db_size","created_at","actions"]
}
```

Blackbox can transform these into React pages with Tailwind classes.

---

## 22 — Handover checklist for Blackbox

1. Create repo root with above `NAKSHA_CLOUD_SPEC.md`.
2. Generate `docker-compose.dev.yml` from JSON block.
3. Create `backend` service scaffold with Prisma schema matching SQL above and migration scripts.
4. Implement Auth service (GoTrue preferred). If unavailable, build Express JWT auth.
5. Provision Hasura metadata for GraphQL and RLS. Provide script `infra/scripts/hasura_apply_metadata.sh`.
6. Implement storage presign endpoints.
7. Implement realtime service that listens to Postgres `NOTIFY` and serves WebSocket clients.
8. Generate Admin UI pages per wireframes.
9. Implement SDK wrapper.
10. Add CI to run e2e tests.

---

## 23 — Final machine-readable summary (single JSON)

```json
{
  "project":"Naksha Cloud - Supabase-like MVP",
  "deliverables":["docker-compose.dev.yml","migrations","auth","hasura-metadata","minio","realtime","admin-ui","sdk","e2e-tests","ci-workflow"],
  "runCommands":["cp .env.example .env","docker compose up --build -d","infra/scripts/create_workspace.sh <name> <owner_email>","run e2e tests"]
}
