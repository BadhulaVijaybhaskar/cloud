-- Add tenant_id to existing tables
ALTER TABLE workflow_runs ADD COLUMN tenant_id VARCHAR(255) NOT NULL DEFAULT 'default';
ALTER TABLE workflows ADD COLUMN tenant_id VARCHAR(255) NOT NULL DEFAULT 'default';

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'
);

-- Insert default tenant
INSERT INTO tenants (id, name) VALUES ('default', 'Default Tenant') ON CONFLICT DO NOTHING;

-- Enable RLS on tables
ALTER TABLE workflow_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY workflow_runs_tenant_policy ON workflow_runs
    FOR ALL TO PUBLIC
    USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY workflows_tenant_policy ON workflows  
    FOR ALL TO PUBLIC
    USING (tenant_id = current_setting('app.current_tenant', true));

-- Create indexes for tenant queries
CREATE INDEX idx_workflow_runs_tenant_id ON workflow_runs(tenant_id);
CREATE INDEX idx_workflows_tenant_id ON workflows(tenant_id);