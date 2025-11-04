-- ATOM Marketplace Database Schema - J.3 Specification
-- Models and versions tables per spec

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Models table (simplified per spec)
CREATE TABLE models (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  vendor_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  license TEXT NOT NULL,
  tags TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  status TEXT DEFAULT 'active',
  latest_version TEXT,
  UNIQUE(vendor_id, name)
);

-- Model versions table per spec
CREATE TABLE model_versions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_id UUID REFERENCES models(id) ON DELETE CASCADE,
  version TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  checksum TEXT NOT NULL,
  size_mb INT,
  metadata JSONB,
  published_at TIMESTAMP DEFAULT NOW(),
  governance_status TEXT DEFAULT 'pending',
  UNIQUE(model_id, version)
);

-- Agents table
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  vendor_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  execution_policy JSONB NOT NULL,
  capabilities TEXT[],
  resource_requirements JSONB,
  safety_constraints JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  status TEXT DEFAULT 'registered',
  governance_status TEXT DEFAULT 'pending'
);

-- Agent test runs
CREATE TABLE agent_test_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  status TEXT DEFAULT 'running',
  config JSONB,
  result JSONB,
  execution_time_ms INT
);

-- Marketplace transactions
CREATE TABLE marketplace_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_id UUID REFERENCES models(id),
  agent_id UUID REFERENCES agents(id),
  user_id UUID NOT NULL,
  transaction_type TEXT NOT NULL, -- 'download', 'usage', 'subscription'
  amount_cents INT,
  currency TEXT DEFAULT 'USD',
  created_at TIMESTAMP DEFAULT NOW(),
  status TEXT DEFAULT 'completed'
);

-- Billing events
CREATE TABLE billing_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id TEXT NOT NULL,
  model_id UUID,
  agent_id UUID,
  event_type TEXT NOT NULL,
  units INT DEFAULT 1,
  cost_center TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_models_vendor ON models(vendor_id);
CREATE INDEX idx_models_tags ON models USING GIN(tags);
CREATE INDEX idx_model_versions_model ON model_versions(model_id);
CREATE INDEX idx_agents_vendor ON agents(vendor_id);
CREATE INDEX idx_agents_capabilities ON agents USING GIN(capabilities);
CREATE INDEX idx_billing_events_project ON billing_events(project_id);
CREATE INDEX idx_billing_events_created ON billing_events(created_at);

-- Sample data for simulation
INSERT INTO models (vendor_id, name, description, license, tags, latest_version) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'ATOM Neural Optimizer', 'AI-powered performance optimization engine', 'MIT', ARRAY['ai', 'optimization', 'performance'], '2.1.0'),
  ('550e8400-e29b-41d4-a716-446655440001', 'Quantum Crypto Engine', 'Post-quantum cryptography implementation', 'Apache-2.0', ARRAY['security', 'quantum', 'encryption'], '1.5.0'),
  ('550e8400-e29b-41d4-a716-446655440002', 'Smart Analytics Agent', 'Autonomous data analysis and insights', 'proprietary', ARRAY['analytics', 'ai', 'insights'], '3.0.0');

INSERT INTO model_versions (model_id, version, artifact_path, checksum, size_mb, governance_status) VALUES
  ((SELECT id FROM models WHERE name = 'ATOM Neural Optimizer'), '2.1.0', 's3://atom-models/neural-optimizer/2.1.0/model.tar.gz', 'sha256:abc123...', 150, 'approved'),
  ((SELECT id FROM models WHERE name = 'Quantum Crypto Engine'), '1.5.0', 's3://atom-models/quantum-crypto/1.5.0/engine.tar.gz', 'sha256:def456...', 75, 'approved'),
  ((SELECT id FROM models WHERE name = 'Smart Analytics Agent'), '3.0.0', 's3://atom-models/analytics-agent/3.0.0/agent.tar.gz', 'sha256:ghi789...', 200, 'approved');