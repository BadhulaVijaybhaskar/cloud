-- infra/sql/aol_schema.sql
CREATE TABLE IF NOT EXISTS aol_recommendations (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  type TEXT NOT NULL,
  payload JSONB,
  status TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  pre_hash TEXT,
  post_hash TEXT,
  simulation_result JSONB
);

CREATE TABLE IF NOT EXISTS aol_executions (
  id TEXT PRIMARY KEY,
  recommendation_id TEXT REFERENCES aol_recommendations(id),
  mode TEXT,
  status TEXT,
  started_at TIMESTAMP WITH TIME ZONE,
  finished_at TIMESTAMP WITH TIME ZONE,
  logs JSONB
);

CREATE TABLE IF NOT EXISTS aol_policy_decisions (
  id TEXT PRIMARY KEY,
  rec_id TEXT REFERENCES aol_recommendations(id),
  decision JSONB,
  evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);