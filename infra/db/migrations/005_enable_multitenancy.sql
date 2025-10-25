-- Migration 005: Enable Multi-Tenancy and RBAC
-- Phase C.3 - Multi-Tenant Schema & RBAC
-- Adds tenant isolation and role-based access control

-- Enable Row Level Security
ALTER TABLE workflow_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE insight_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE perf_metrics ENABLE ROW LEVEL SECURITY;

-- Add tenant_id columns to existing tables
ALTER TABLE workflow_runs ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE insight_signals ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE perf_metrics ADD COLUMN IF NOT EXISTS tenant_id UUID;

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    active BOOLEAN DEFAULT true,
    
    -- Metadata
    settings JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{"max_users": 100, "max_workflows": 1000}',
    
    CONSTRAINT valid_slug CHECK (slug ~ '^[a-z0-9-]+$')
);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]',
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(name, tenant_id)
);

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID,
    
    UNIQUE(user_id, role_id, tenant_id)
);

-- Insert default roles
INSERT INTO roles (name, description, permissions, tenant_id) VALUES
('admin', 'Full administrative access', '["*"]', NULL),
('operator', 'Operational access to workflows and monitoring', '["workflows:read", "workflows:write", "metrics:read", "predictions:read"]', NULL),
('viewer', 'Read-only access to dashboards and reports', '["workflows:read", "metrics:read", "reports:read"]', NULL)
ON CONFLICT DO NOTHING;

-- Create RLS policies for workflow_runs
DROP POLICY IF EXISTS tenant_isolation_workflow_runs ON workflow_runs;
CREATE POLICY tenant_isolation_workflow_runs ON workflow_runs
    FOR ALL
    TO authenticated
    USING (
        tenant_id = COALESCE(
            (current_setting('app.current_tenant_id', true))::uuid,
            (current_setting('jwt.claims.tenant_id', true))::uuid
        )
    );

-- Create RLS policies for insight_signals  
DROP POLICY IF EXISTS tenant_isolation_insight_signals ON insight_signals;
CREATE POLICY tenant_isolation_insight_signals ON insight_signals
    FOR ALL
    TO authenticated
    USING (
        tenant_id = COALESCE(
            (current_setting('app.current_tenant_id', true))::uuid,
            (current_setting('jwt.claims.tenant_id', true))::uuid
        )
    );

-- Create RLS policies for predictions
DROP POLICY IF EXISTS tenant_isolation_predictions ON predictions;
CREATE POLICY tenant_isolation_predictions ON predictions
    FOR ALL
    TO authenticated
    USING (
        tenant_id = COALESCE(
            (current_setting('app.current_tenant_id', true))::uuid,
            (current_setting('jwt.claims.tenant_id', true))::uuid
        )
    );

-- Create RLS policies for perf_metrics
DROP POLICY IF EXISTS tenant_isolation_perf_metrics ON perf_metrics;
CREATE POLICY tenant_isolation_perf_metrics ON perf_metrics
    FOR ALL
    TO authenticated
    USING (
        tenant_id = COALESCE(
            (current_setting('app.current_tenant_id', true))::uuid,
            (current_setting('jwt.claims.tenant_id', true))::uuid
        )
    );

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_runs_tenant_id ON workflow_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_insight_signals_tenant_id ON insight_signals(tenant_id);
CREATE INDEX IF NOT EXISTS idx_predictions_tenant_id ON predictions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_perf_metrics_tenant_id ON perf_metrics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_tenant_id ON user_roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);

-- Create function to check user permissions
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id UUID,
    p_tenant_id UUID,
    p_permission TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    has_permission BOOLEAN := FALSE;
BEGIN
    -- Check if user has the specific permission or wildcard
    SELECT EXISTS(
        SELECT 1 
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = p_user_id 
        AND ur.tenant_id = p_tenant_id
        AND (
            r.permissions ? p_permission 
            OR r.permissions ? '*'
        )
    ) INTO has_permission;
    
    RETURN has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to set tenant context
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id UUID) RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', p_tenant_id::text, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create view for user permissions
CREATE OR REPLACE VIEW user_permissions AS
SELECT 
    ur.user_id,
    ur.tenant_id,
    t.name as tenant_name,
    r.name as role_name,
    r.permissions,
    ur.granted_at
FROM user_roles ur
JOIN roles r ON ur.role_id = r.id
JOIN tenants t ON ur.tenant_id = t.id
WHERE t.active = true;

-- Create default tenant for existing data
INSERT INTO tenants (id, name, slug) VALUES 
('00000000-0000-0000-0000-000000000001', 'Default Tenant', 'default')
ON CONFLICT DO NOTHING;

-- Update existing records to use default tenant
UPDATE workflow_runs SET tenant_id = '00000000-0000-0000-0000-000000000001' WHERE tenant_id IS NULL;
UPDATE insight_signals SET tenant_id = '00000000-0000-0000-0000-000000000001' WHERE tenant_id IS NULL;
UPDATE predictions SET tenant_id = '00000000-0000-0000-0000-000000000001' WHERE tenant_id IS NULL;
UPDATE perf_metrics SET tenant_id = '00000000-0000-0000-0000-000000000001' WHERE tenant_id IS NULL;

COMMENT ON TABLE tenants IS 'Multi-tenant organizations with isolation';
COMMENT ON TABLE roles IS 'Role-based access control definitions';
COMMENT ON TABLE user_roles IS 'User role assignments per tenant';
COMMENT ON FUNCTION check_user_permission IS 'Validates user permissions for tenant operations';