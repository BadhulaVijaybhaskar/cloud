# Naksha Cloud

A Supabase-like backend platform MVP with multi-tenant Postgres, Auth, Storage, Realtime, GraphQL API, and Admin UI.

## Quick Start

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in secrets
3. Run `docker compose up --build -d`
4. Run setup: `infra/scripts/setup.sh`
5. Create a workspace: `infra/scripts/create_workspace.sh "My Workspace" user@example.com`
6. Open Admin UI at http://localhost:3000

## Architecture

- **Postgres**: Multi-tenant database with schema-per-tenant
- **Hasura**: GraphQL API with RLS
- **Auth Service**: JWT-based authentication
- **MinIO**: S3-compatible storage
- **Realtime Service**: WebSocket for live updates
- **Admin UI**: React/Next.js interface

## API Endpoints

- Auth: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Storage: `POST /storage/presign`, `GET /storage/:workspace/list`
- GraphQL: `POST /v1/graphql` (Hasura)
- Realtime: `ws://:4000`

## SDK Usage

```typescript
import { createClient } from 'naksha-sdk';

const client = createClient('http://localhost:3000', token);

// Auth
await client.login('user@example.com', 'password');

// CRUD
await client.from('projects').select().insert({ name: 'New Project' });

// Realtime
const realtime = client.realtime.connect({ token, workspace: 'ws-id' });
realtime.on('event', (msg) => console.log(msg));
```

## Development

- Backend: `cd backend && npm install && npm run dev`
- Auth: `cd services/auth && npm install && npm run dev`
- Realtime: `cd services/realtime && npm install && npm run dev`
- Admin UI: `cd admin && npm install && npm run dev`
- SDK: `cd sdk && npm install && npm run build`

## Testing

Run E2E tests: `cd e2e-tests && node test.js`

## Deployment

See `docker-compose.dev.yml` for local dev. For production, use managed Postgres, S3, etc.
