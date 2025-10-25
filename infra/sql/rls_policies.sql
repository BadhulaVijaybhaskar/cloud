-- Example RLS
ALTER TABLE workflow_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON workflow_runs
USING (tenant_id = current_setting('app.current_tenant')::uuid);
