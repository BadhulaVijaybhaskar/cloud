-- Migration 001: Create workflow_runs table
-- Stores LangGraph workflow execution history

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wpk_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    inputs JSONB,
    outputs JSONB,
    status TEXT NOT NULL,
    duration_ms INTEGER,
    node_logs JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX idx_workflow_runs_wpk_id ON workflow_runs(wpk_id);
CREATE INDEX idx_workflow_runs_run_id ON workflow_runs(run_id);
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_created_at ON workflow_runs(created_at DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workflow_runs_updated_at 
    BEFORE UPDATE ON workflow_runs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();