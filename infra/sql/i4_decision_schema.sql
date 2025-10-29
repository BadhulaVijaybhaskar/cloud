-- Phase I.4 Collective Reasoning & Federated Decision Fabric Database Schema
-- Supports multi-tenant decision storage with audit trails and snapshots

-- Decision Proposals Table
CREATE TABLE IF NOT EXISTS decision_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id VARCHAR(255) UNIQUE NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    manifest JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'submitted',
    impact_level VARCHAR(20) DEFAULT 'medium',
    pre_state_hash VARCHAR(64),
    post_state_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Decision Negotiations Table
CREATE TABLE IF NOT EXISTS decision_negotiations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    negotiation_id VARCHAR(255) UNIQUE NOT NULL,
    proposal_id VARCHAR(255) NOT NULL REFERENCES decision_proposals(proposal_id),
    regions TEXT[] NOT NULL,
    quorum_threshold DECIMAL(3,2) DEFAULT 0.6,
    status VARCHAR(50) DEFAULT 'active',
    consensus_reached BOOLEAN DEFAULT FALSE,
    consensus_ratio DECIMAL(3,2),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    timeout_at TIMESTAMP WITH TIME ZONE
);

-- Regional Votes Table
CREATE TABLE IF NOT EXISTS regional_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    negotiation_id VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    vote VARCHAR(20) NOT NULL, -- 'approve', 'reject', 'abstain'
    weight DECIMAL(3,2) DEFAULT 1.0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (negotiation_id) REFERENCES decision_negotiations(negotiation_id),
    UNIQUE(negotiation_id, region)
);

-- Confidence Scores Table
CREATE TABLE IF NOT EXISTS confidence_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id VARCHAR(255) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    risk DECIMAL(3,2) NOT NULL,
    cost_estimate DECIMAL(10,2),
    explanation TEXT,
    factors JSONB DEFAULT '{}',
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (proposal_id) REFERENCES decision_proposals(proposal_id)
);

-- Approvals Table
CREATE TABLE IF NOT EXISTS decision_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id VARCHAR(255) NOT NULL,
    approver_id VARCHAR(255) NOT NULL,
    approver_name VARCHAR(255),
    decision VARCHAR(20) NOT NULL, -- 'approve', 'reject'
    reason TEXT,
    mfa_verified BOOLEAN DEFAULT FALSE,
    signature VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (proposal_id) REFERENCES decision_proposals(proposal_id)
);

-- State Snapshots Table
CREATE TABLE IF NOT EXISTS state_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id VARCHAR(255) UNIQUE NOT NULL,
    proposal_id VARCHAR(255) NOT NULL,
    snapshot_type VARCHAR(10) NOT NULL, -- 'pre', 'post'
    state_data JSONB NOT NULL,
    state_hash VARCHAR(64) NOT NULL,
    pqc_signature TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (proposal_id) REFERENCES decision_proposals(proposal_id)
);

-- Audit Trail Table
CREATE TABLE IF NOT EXISTS decision_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id VARCHAR(255) UNIQUE NOT NULL,
    proposal_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    details JSONB DEFAULT '{}',
    audit_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (proposal_id) REFERENCES decision_proposals(proposal_id)
);

-- Canary Runs Table
CREATE TABLE IF NOT EXISTS canary_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canary_id VARCHAR(255) UNIQUE NOT NULL,
    proposal_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    dry_run BOOLEAN DEFAULT TRUE,
    canary_percentage DECIMAL(5,2) DEFAULT 10.0,
    rollback_threshold DECIMAL(5,4) DEFAULT 0.05,
    success_rate DECIMAL(5,4),
    error_rate DECIMAL(5,4),
    metrics JSONB DEFAULT '{}',
    recommendation VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (proposal_id) REFERENCES decision_proposals(proposal_id)
);

-- Rollback Plans Table
CREATE TABLE IF NOT EXISTS rollback_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rollback_id VARCHAR(255) UNIQUE NOT NULL,
    proposal_id VARCHAR(255) NOT NULL,
    target_snapshot VARCHAR(255) NOT NULL,
    target_state_hash VARCHAR(64) NOT NULL,
    dry_run BOOLEAN DEFAULT TRUE,
    steps JSONB DEFAULT '[]',
    estimated_duration VARCHAR(50),
    risk_level VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (proposal_id) REFERENCES decision_proposals(proposal_id),
    FOREIGN KEY (target_snapshot) REFERENCES state_snapshots(snapshot_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_proposals_tenant ON decision_proposals(tenant_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON decision_proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_impact ON decision_proposals(impact_level);
CREATE INDEX IF NOT EXISTS idx_negotiations_proposal ON decision_negotiations(proposal_id);
CREATE INDEX IF NOT EXISTS idx_negotiations_status ON decision_negotiations(status);
CREATE INDEX IF NOT EXISTS idx_votes_negotiation ON regional_votes(negotiation_id);
CREATE INDEX IF NOT EXISTS idx_votes_region ON regional_votes(region);
CREATE INDEX IF NOT EXISTS idx_scores_proposal ON confidence_scores(proposal_id);
CREATE INDEX IF NOT EXISTS idx_approvals_proposal ON decision_approvals(proposal_id);
CREATE INDEX IF NOT EXISTS idx_approvals_approver ON decision_approvals(approver_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_proposal ON state_snapshots(proposal_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_type ON state_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_audit_proposal ON decision_audit_trail(proposal_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON decision_audit_trail(action);
CREATE INDEX IF NOT EXISTS idx_canary_proposal ON canary_runs(proposal_id);
CREATE INDEX IF NOT EXISTS idx_rollback_proposal ON rollback_plans(proposal_id);

-- GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_proposals_manifest_gin ON decision_proposals USING GIN(manifest);
CREATE INDEX IF NOT EXISTS idx_proposals_metadata_gin ON decision_proposals USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_scores_factors_gin ON confidence_scores USING GIN(factors);
CREATE INDEX IF NOT EXISTS idx_snapshots_data_gin ON state_snapshots USING GIN(state_data);
CREATE INDEX IF NOT EXISTS idx_audit_details_gin ON decision_audit_trail USING GIN(details);
CREATE INDEX IF NOT EXISTS idx_canary_metrics_gin ON canary_runs USING GIN(metrics);

-- Row Level Security (RLS) for multi-tenancy
ALTER TABLE decision_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE decision_negotiations ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE confidence_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE decision_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE state_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE decision_audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE canary_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rollback_plans ENABLE ROW LEVEL SECURITY;

-- RLS Policies (tenant isolation)
CREATE POLICY decision_proposals_tenant_isolation ON decision_proposals
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY decision_negotiations_tenant_isolation ON decision_negotiations
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY regional_votes_tenant_isolation ON regional_votes
    FOR ALL USING (
        negotiation_id IN (
            SELECT n.negotiation_id FROM decision_negotiations n
            JOIN decision_proposals p ON n.proposal_id = p.proposal_id
            WHERE p.tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY confidence_scores_tenant_isolation ON confidence_scores
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY decision_approvals_tenant_isolation ON decision_approvals
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY state_snapshots_tenant_isolation ON state_snapshots
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY decision_audit_tenant_isolation ON decision_audit_trail
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY canary_runs_tenant_isolation ON canary_runs
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY rollback_plans_tenant_isolation ON rollback_plans
    FOR ALL USING (
        proposal_id IN (
            SELECT proposal_id FROM decision_proposals 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

-- Functions for decision operations
CREATE OR REPLACE FUNCTION update_decision_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_proposals_timestamp
    BEFORE UPDATE ON decision_proposals
    FOR EACH ROW EXECUTE FUNCTION update_decision_timestamp();

-- Function to calculate consensus
CREATE OR REPLACE FUNCTION calculate_consensus(
    p_negotiation_id VARCHAR(255)
)
RETURNS TABLE(
    consensus_ratio DECIMAL(3,2),
    consensus_reached BOOLEAN
) AS $$
DECLARE
    v_total_weight DECIMAL(3,2);
    v_approve_weight DECIMAL(3,2);
    v_threshold DECIMAL(3,2);
    v_ratio DECIMAL(3,2);
    v_reached BOOLEAN;
BEGIN
    -- Get negotiation threshold
    SELECT quorum_threshold INTO v_threshold
    FROM decision_negotiations
    WHERE negotiation_id = p_negotiation_id;
    
    -- Calculate total weight
    SELECT COALESCE(SUM(weight), 0) INTO v_total_weight
    FROM regional_votes
    WHERE negotiation_id = p_negotiation_id;
    
    -- Calculate approve weight
    SELECT COALESCE(SUM(weight), 0) INTO v_approve_weight
    FROM regional_votes
    WHERE negotiation_id = p_negotiation_id AND vote = 'approve';
    
    -- Calculate ratio and consensus
    IF v_total_weight > 0 THEN
        v_ratio := v_approve_weight / v_total_weight;
        v_reached := v_ratio >= v_threshold;
    ELSE
        v_ratio := 0;
        v_reached := FALSE;
    END IF;
    
    RETURN QUERY SELECT v_ratio, v_reached;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE decision_proposals IS 'Core decision proposals in the federated decision fabric';
COMMENT ON TABLE decision_negotiations IS 'Multi-region negotiation sessions for proposals';
COMMENT ON TABLE regional_votes IS 'Votes from regional agents in negotiations';
COMMENT ON TABLE confidence_scores IS 'AI-generated confidence and risk scores for proposals';
COMMENT ON TABLE decision_approvals IS 'Human approvals for high-impact decisions';
COMMENT ON TABLE state_snapshots IS 'Pre/post state snapshots for rollback capability';
COMMENT ON TABLE decision_audit_trail IS 'Immutable audit trail for all decision operations';
COMMENT ON TABLE canary_runs IS 'Canary deployment validation results';
COMMENT ON TABLE rollback_plans IS 'Rollback plans and execution records';