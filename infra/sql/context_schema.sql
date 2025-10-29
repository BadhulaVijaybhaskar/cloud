-- Phase I.3 Global Contextual Intelligence Database Schema
-- Supports multi-tenant context storage with temporal tracking

-- Context Entities Table
CREATE TABLE IF NOT EXISTS context_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, entity_id)
);

-- Context States Table (current state)
CREATE TABLE IF NOT EXISTS context_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_uuid UUID NOT NULL REFERENCES context_entities(id) ON DELETE CASCADE,
    context_data JSONB NOT NULL,
    context_hash VARCHAR(64) NOT NULL,
    sources TEXT[] DEFAULT '{}',
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    region VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Context History Table (temporal snapshots)
CREATE TABLE IF NOT EXISTS context_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_uuid UUID NOT NULL REFERENCES context_entities(id) ON DELETE CASCADE,
    context_data JSONB NOT NULL,
    snapshot_hash VARCHAR(64) NOT NULL,
    snapshot_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    drift_score DECIMAL(3,2) DEFAULT 0.0,
    changed_keys TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Context Patterns Table
CREATE TABLE IF NOT EXISTS context_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100) NOT NULL,
    entities UUID[] NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    description TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, pattern_id)
);

-- Context Reasoning Results Table
CREATE TABLE IF NOT EXISTS context_reasoning (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_uuid UUID NOT NULL REFERENCES context_entities(id) ON DELETE CASCADE,
    reasoning_type VARCHAR(50) NOT NULL,
    predictions JSONB NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    reasoning_steps TEXT[] DEFAULT '{}',
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Context Audit Log Table
CREATE TABLE IF NOT EXISTS context_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_uuid UUID NOT NULL REFERENCES context_entities(id) ON DELETE CASCADE,
    operation VARCHAR(50) NOT NULL,
    compliance_status VARCHAR(20) NOT NULL,
    violations JSONB DEFAULT '[]',
    bias_score DECIMAL(3,2) DEFAULT 0.0,
    audit_hash VARCHAR(64) NOT NULL,
    audited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Context Routing Log Table
CREATE TABLE IF NOT EXISTS context_routing_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_uuid UUID NOT NULL REFERENCES context_entities(id) ON DELETE CASCADE,
    target_regions TEXT[] NOT NULL,
    routed_regions TEXT[] DEFAULT '{}',
    failed_regions TEXT[] DEFAULT '{}',
    routing_hash VARCHAR(64) NOT NULL,
    routed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_context_entities_tenant ON context_entities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_context_entities_entity_id ON context_entities(entity_id);
CREATE INDEX IF NOT EXISTS idx_context_states_entity ON context_states(entity_uuid);
CREATE INDEX IF NOT EXISTS idx_context_states_region ON context_states(region);
CREATE INDEX IF NOT EXISTS idx_context_states_relevance ON context_states(relevance_score);
CREATE INDEX IF NOT EXISTS idx_context_history_entity ON context_history(entity_uuid);
CREATE INDEX IF NOT EXISTS idx_context_history_timestamp ON context_history(snapshot_timestamp);
CREATE INDEX IF NOT EXISTS idx_context_patterns_tenant ON context_patterns(tenant_id);
CREATE INDEX IF NOT EXISTS idx_context_reasoning_entity ON context_reasoning(entity_uuid);
CREATE INDEX IF NOT EXISTS idx_context_audit_entity ON context_audit_log(entity_uuid);
CREATE INDEX IF NOT EXISTS idx_context_audit_status ON context_audit_log(compliance_status);
CREATE INDEX IF NOT EXISTS idx_context_routing_entity ON context_routing_log(entity_uuid);

-- GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_context_states_data_gin ON context_states USING GIN(context_data);
CREATE INDEX IF NOT EXISTS idx_context_history_data_gin ON context_history USING GIN(context_data);
CREATE INDEX IF NOT EXISTS idx_context_reasoning_predictions_gin ON context_reasoning USING GIN(predictions);

-- Row Level Security (RLS) for multi-tenancy
ALTER TABLE context_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_reasoning ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_routing_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies (tenant isolation)
CREATE POLICY context_entities_tenant_isolation ON context_entities
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY context_states_tenant_isolation ON context_states
    FOR ALL USING (
        entity_uuid IN (
            SELECT id FROM context_entities 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY context_history_tenant_isolation ON context_history
    FOR ALL USING (
        entity_uuid IN (
            SELECT id FROM context_entities 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY context_patterns_tenant_isolation ON context_patterns
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY context_reasoning_tenant_isolation ON context_reasoning
    FOR ALL USING (
        entity_uuid IN (
            SELECT id FROM context_entities 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY context_audit_tenant_isolation ON context_audit_log
    FOR ALL USING (
        entity_uuid IN (
            SELECT id FROM context_entities 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

CREATE POLICY context_routing_tenant_isolation ON context_routing_log
    FOR ALL USING (
        entity_uuid IN (
            SELECT id FROM context_entities 
            WHERE tenant_id = current_setting('app.current_tenant', true)
        )
    );

-- Functions for context operations
CREATE OR REPLACE FUNCTION update_context_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_context_entities_timestamp
    BEFORE UPDATE ON context_entities
    FOR EACH ROW EXECUTE FUNCTION update_context_timestamp();

CREATE TRIGGER update_context_states_timestamp
    BEFORE UPDATE ON context_states
    FOR EACH ROW EXECUTE FUNCTION update_context_timestamp();

-- Function to calculate context drift
CREATE OR REPLACE FUNCTION calculate_context_drift(
    p_entity_uuid UUID,
    p_window_minutes INTEGER DEFAULT 60
)
RETURNS TABLE(
    drift_score DECIMAL(3,2),
    changed_keys TEXT[],
    trend VARCHAR(20)
) AS $$
DECLARE
    v_snapshots RECORD;
    v_first_context JSONB;
    v_last_context JSONB;
    v_all_keys TEXT[];
    v_changed_keys TEXT[];
    v_drift_score DECIMAL(3,2);
    v_trend VARCHAR(20);
BEGIN
    -- Get snapshots within time window
    SELECT 
        array_agg(context_data ORDER BY snapshot_timestamp) as contexts
    INTO v_snapshots
    FROM context_history
    WHERE entity_uuid = p_entity_uuid
    AND snapshot_timestamp > NOW() - INTERVAL '1 minute' * p_window_minutes;
    
    -- Return empty if insufficient data
    IF array_length(v_snapshots.contexts, 1) < 2 THEN
        RETURN QUERY SELECT 0.0::DECIMAL(3,2), '{}'::TEXT[], 'stable'::VARCHAR(20);
        RETURN;
    END IF;
    
    -- Get first and last contexts
    v_first_context := v_snapshots.contexts[1];
    v_last_context := v_snapshots.contexts[array_length(v_snapshots.contexts, 1)];
    
    -- Calculate changed keys (simplified)
    SELECT array_agg(DISTINCT key)
    INTO v_all_keys
    FROM (
        SELECT jsonb_object_keys(v_first_context) as key
        UNION
        SELECT jsonb_object_keys(v_last_context) as key
    ) keys;
    
    -- Calculate drift score (simplified)
    v_drift_score := 0.5; -- Mock calculation
    
    -- Determine trend
    IF v_drift_score > 0.5 THEN
        v_trend := 'volatile';
    ELSIF v_drift_score > 0.2 THEN
        v_trend := 'evolving';
    ELSE
        v_trend := 'stable';
    END IF;
    
    RETURN QUERY SELECT v_drift_score, v_all_keys, v_trend;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE context_entities IS 'Core entities tracked in contextual intelligence system';
COMMENT ON TABLE context_states IS 'Current context state for each entity';
COMMENT ON TABLE context_history IS 'Temporal snapshots of context changes';
COMMENT ON TABLE context_patterns IS 'Detected patterns across entities';
COMMENT ON TABLE context_reasoning IS 'AI reasoning results and predictions';
COMMENT ON TABLE context_audit_log IS 'Policy compliance audit trail';
COMMENT ON TABLE context_routing_log IS 'Context routing operations log';