-- AOL (Adaptive Optimization Layer) Database Schema
-- Phase I.6 - Database tables for optimization proposals and audit

-- Optimization proposals table
CREATE TABLE IF NOT EXISTS aol_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope VARCHAR(255) NOT NULL,
    changes JSONB NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    status VARCHAR(50) NOT NULL DEFAULT 'proposed',
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL DEFAULT 'aol-system',
    pre_state_hash VARCHAR(64),
    post_state_hash VARCHAR(64),
    approver VARCHAR(255),
    audit_ref UUID,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Canary deployment runs table
CREATE TABLE IF NOT EXISTS aol_canary_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES aol_proposals(id),
    canary_id VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    results JSONB,
    rollback_plan JSONB,
    execution_log JSONB
);

-- Metrics snapshots for evaluation
CREATE TABLE IF NOT EXISTS aol_metrics_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant VARCHAR(255),
    metric_name VARCHAR(100) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    summary JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for P7 compliance (immutable)
CREATE TABLE IF NOT EXISTS aol_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    proposal_id UUID REFERENCES aol_proposals(id),
    event_data JSONB NOT NULL,
    signature JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Optimization history for learning
CREATE TABLE IF NOT EXISTS aol_optimization_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES aol_proposals(id),
    metric_name VARCHAR(100) NOT NULL,
    baseline_value DECIMAL(10,4),
    optimized_value DECIMAL(10,4),
    improvement_percent DECIMAL(6,2),
    measurement_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_aol_proposals_scope ON aol_proposals(scope);
CREATE INDEX IF NOT EXISTS idx_aol_proposals_status ON aol_proposals(status);
CREATE INDEX IF NOT EXISTS idx_aol_proposals_created_at ON aol_proposals(created_at);
CREATE INDEX IF NOT EXISTS idx_aol_proposals_risk_level ON aol_proposals(risk_level);

CREATE INDEX IF NOT EXISTS idx_aol_canary_runs_proposal_id ON aol_canary_runs(proposal_id);
CREATE INDEX IF NOT EXISTS idx_aol_canary_runs_status ON aol_canary_runs(status);
CREATE INDEX IF NOT EXISTS idx_aol_canary_runs_started_at ON aol_canary_runs(started_at);

CREATE INDEX IF NOT EXISTS idx_aol_metrics_snapshot_tenant ON aol_metrics_snapshot(tenant);
CREATE INDEX IF NOT EXISTS idx_aol_metrics_snapshot_metric_name ON aol_metrics_snapshot(metric_name);
CREATE INDEX IF NOT EXISTS idx_aol_metrics_snapshot_window_start ON aol_metrics_snapshot(window_start);

CREATE INDEX IF NOT EXISTS idx_aol_audit_log_event_type ON aol_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_aol_audit_log_proposal_id ON aol_audit_log(proposal_id);
CREATE INDEX IF NOT EXISTS idx_aol_audit_log_created_at ON aol_audit_log(created_at);

CREATE INDEX IF NOT EXISTS idx_aol_optimization_history_proposal_id ON aol_optimization_history(proposal_id);
CREATE INDEX IF NOT EXISTS idx_aol_optimization_history_metric_name ON aol_optimization_history(metric_name);

-- Row Level Security (RLS) for P5 Multi-tenancy
ALTER TABLE aol_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE aol_metrics_snapshot ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY aol_proposals_tenant_isolation ON aol_proposals
    FOR ALL
    USING (
        scope LIKE 'tenant:' || current_setting('app.current_tenant', true) || '%'
        OR scope = 'global'
        OR current_setting('app.current_tenant', true) = 'admin'
    );

CREATE POLICY aol_metrics_tenant_isolation ON aol_metrics_snapshot
    FOR ALL
    USING (
        tenant = current_setting('app.current_tenant', true)
        OR tenant IS NULL
        OR current_setting('app.current_tenant', true) = 'admin'
    );

-- Audit log is append-only for P7 compliance
CREATE POLICY aol_audit_log_append_only ON aol_audit_log
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY aol_audit_log_read_only ON aol_audit_log
    FOR SELECT
    USING (true);

-- Functions for optimization metrics
CREATE OR REPLACE FUNCTION calculate_optimization_improvement(
    p_proposal_id UUID,
    p_metric_name VARCHAR(100)
) RETURNS DECIMAL(6,2) AS $$
DECLARE
    baseline_avg DECIMAL(10,4);
    optimized_avg DECIMAL(10,4);
    improvement DECIMAL(6,2);
BEGIN
    -- Get baseline average (before optimization)
    SELECT AVG(baseline_value) INTO baseline_avg
    FROM aol_optimization_history
    WHERE proposal_id = p_proposal_id AND metric_name = p_metric_name;
    
    -- Get optimized average (after optimization)
    SELECT AVG(optimized_value) INTO optimized_avg
    FROM aol_optimization_history
    WHERE proposal_id = p_proposal_id AND metric_name = p_metric_name;
    
    -- Calculate improvement percentage
    IF baseline_avg > 0 THEN
        improvement := ((optimized_avg - baseline_avg) / baseline_avg) * 100;
    ELSE
        improvement := 0;
    END IF;
    
    RETURN improvement;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update proposal status based on canary results
CREATE OR REPLACE FUNCTION update_proposal_from_canary() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'success' THEN
        UPDATE aol_proposals 
        SET status = 'applied', updated_at = NOW()
        WHERE id = NEW.proposal_id;
    ELSIF NEW.status = 'failed' THEN
        UPDATE aol_proposals 
        SET status = 'rejected', updated_at = NOW()
        WHERE id = NEW.proposal_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_proposal_from_canary
    AFTER UPDATE ON aol_canary_runs
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION update_proposal_from_canary();

-- View for optimization dashboard
CREATE OR REPLACE VIEW aol_optimization_dashboard AS
SELECT 
    p.id,
    p.scope,
    p.risk_level,
    p.status,
    p.created_at,
    p.approver,
    COALESCE(c.status, 'not_started') as canary_status,
    c.started_at as canary_started_at,
    c.finished_at as canary_finished_at,
    (
        SELECT COUNT(*)
        FROM aol_optimization_history h
        WHERE h.proposal_id = p.id
    ) as metrics_count,
    (
        SELECT AVG(improvement_percent)
        FROM aol_optimization_history h
        WHERE h.proposal_id = p.id
    ) as avg_improvement_percent
FROM aol_proposals p
LEFT JOIN aol_canary_runs c ON p.id = c.proposal_id
ORDER BY p.created_at DESC;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON aol_proposals TO aol_service;
GRANT SELECT, INSERT, UPDATE ON aol_canary_runs TO aol_service;
GRANT SELECT, INSERT ON aol_metrics_snapshot TO aol_service;
GRANT SELECT, INSERT ON aol_audit_log TO aol_service;
GRANT SELECT, INSERT ON aol_optimization_history TO aol_service;
GRANT SELECT ON aol_optimization_dashboard TO aol_service;

-- Comments for documentation
COMMENT ON TABLE aol_proposals IS 'Optimization proposals with P1-P7 policy compliance';
COMMENT ON TABLE aol_canary_runs IS 'Canary deployment execution tracking';
COMMENT ON TABLE aol_metrics_snapshot IS 'Historical metrics for backtest evaluation';
COMMENT ON TABLE aol_audit_log IS 'Immutable audit log for P7 compliance';
COMMENT ON TABLE aol_optimization_history IS 'Historical optimization results for ML learning';

COMMENT ON COLUMN aol_proposals.pre_state_hash IS 'SHA256 hash of system state before optimization';
COMMENT ON COLUMN aol_proposals.post_state_hash IS 'SHA256 hash of system state after optimization';
COMMENT ON COLUMN aol_audit_log.signature IS 'Cosign signature for P2 compliance';