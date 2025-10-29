-- infra/sql/replication_migrations.sql
CREATE TABLE IF NOT EXISTS replication_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL,
  source TEXT NOT NULL,
  dest TEXT NOT NULL,
  tables JSONB NOT NULL,
  options JSONB,
  status TEXT NOT NULL DEFAULT 'pending',
  data_sha256 TEXT,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS replication_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID,
  action TEXT NOT NULL,            -- e.g. "job_created","snapshot_uploaded","promote"
  actor TEXT,                      -- service or user who triggered
  payload JSONB,
  payload_sha256 TEXT,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS replication_conflicts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID,
  tenant_id TEXT,
  table_name TEXT,
  pk_value JSONB,
  conflict_type TEXT,              -- e.g. "write-write","schema-mismatch"
  details JSONB,
  resolved_by TEXT,
  resolved_at timestamptz
);