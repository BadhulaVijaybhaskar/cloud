-- Migration 007: Create Model Versions and Training Pipeline
-- Phase C.5 - Model Optimization Pipeline
-- Automates model training, versioning, and deployment

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Model versions table
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(100) NOT NULL DEFAULT 'predictive_failure',
    accuracy DECIMAL(5,4) CHECK (accuracy >= 0 AND accuracy <= 1),
    precision_score DECIMAL(5,4) CHECK (precision_score >= 0 AND precision_score <= 1),
    recall_score DECIMAL(5,4) CHECK (recall_score >= 0 AND recall_score <= 1),
    f1_score DECIMAL(5,4) CHECK (f1_score >= 0 AND f1_score <= 1),
    
    -- Model metadata
    training_data_size INTEGER DEFAULT 0,
    training_duration_sec INTEGER DEFAULT 0,
    feature_count INTEGER DEFAULT 0,
    
    -- Model artifacts
    model_path VARCHAR(500),
    model_checksum VARCHAR(64),
    model_signature TEXT, -- Vault signature for P-2 compliance
    
    -- Status and lifecycle
    status VARCHAR(50) DEFAULT 'training' CHECK (status IN ('training', 'validation', 'active', 'deprecated', 'failed')),
    active BOOLEAN DEFAULT FALSE,
    
    -- Performance metrics
    validation_accuracy DECIMAL(5,4),
    test_accuracy DECIMAL(5,4),
    cross_validation_score DECIMAL(5,4),
    
    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activated_at TIMESTAMP WITH TIME ZONE,
    deprecated_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255),
    
    -- Training configuration
    hyperparameters JSONB DEFAULT '{}',
    training_config JSONB DEFAULT '{}'
);

-- Training jobs table
CREATE TABLE IF NOT EXISTS training_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version_id UUID REFERENCES model_versions(id) ON DELETE CASCADE,
    job_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    
    -- Job configuration
    training_data_query TEXT,
    feature_columns JSONB DEFAULT '[]',
    target_column VARCHAR(100),
    
    -- Progress tracking
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    current_step VARCHAR(255),
    total_steps INTEGER DEFAULT 0,
    
    -- Results
    final_accuracy DECIMAL(5,4),
    training_loss DECIMAL(10,6),
    validation_loss DECIMAL(10,6),
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_sec INTEGER,
    
    -- Error handling
    error_message TEXT,
    error_details JSONB,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255)
);

-- Model performance history
CREATE TABLE IF NOT EXISTS model_performance_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version_id UUID REFERENCES model_versions(id) ON DELETE CASCADE,
    
    -- Performance metrics over time
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    
    -- Prediction statistics
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0,
    false_negatives INTEGER DEFAULT 0,
    
    -- Data drift indicators
    feature_drift_score DECIMAL(5,4),
    prediction_drift_score DECIMAL(5,4),
    
    -- Performance period
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    evaluation_dataset_size INTEGER,
    notes TEXT
);

-- Model deployment history
CREATE TABLE IF NOT EXISTS model_deployments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version_id UUID REFERENCES model_versions(id) ON DELETE CASCADE,
    
    -- Deployment details
    deployment_environment VARCHAR(100) DEFAULT 'production',
    deployment_status VARCHAR(50) DEFAULT 'pending' CHECK (deployment_status IN ('pending', 'active', 'rollback', 'failed')),
    
    -- Deployment configuration
    deployment_config JSONB DEFAULT '{}',
    rollback_version_id UUID REFERENCES model_versions(id),
    
    -- Timing
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rollback_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    deployed_by VARCHAR(255),
    deployment_notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_model_versions_active ON model_versions(active, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_versions_type_status ON model_versions(model_type, status);
CREATE INDEX IF NOT EXISTS idx_training_jobs_status ON training_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_model_performance_measured ON model_performance_history(model_version_id, measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_deployments_status ON model_deployments(deployment_status, deployed_at DESC);

-- Views for model management
CREATE OR REPLACE VIEW active_models AS
SELECT 
    mv.id,
    mv.version,
    mv.model_type,
    mv.accuracy,
    mv.precision_score,
    mv.recall_score,
    mv.f1_score,
    mv.created_at,
    mv.activated_at,
    mv.model_path,
    mv.training_data_size,
    
    -- Latest performance
    mph.accuracy as current_accuracy,
    mph.measured_at as last_measured,
    
    -- Deployment status
    md.deployment_status,
    md.deployed_at
    
FROM model_versions mv
LEFT JOIN model_performance_history mph ON mv.id = mph.model_version_id
    AND mph.measured_at = (
        SELECT MAX(measured_at) 
        FROM model_performance_history 
        WHERE model_version_id = mv.id
    )
LEFT JOIN model_deployments md ON mv.id = md.model_version_id
    AND md.deployment_status = 'active'
WHERE mv.active = TRUE
ORDER BY mv.activated_at DESC;

-- View for model comparison
CREATE OR REPLACE VIEW model_comparison AS
SELECT 
    mv.version,
    mv.model_type,
    mv.accuracy,
    mv.precision_score,
    mv.recall_score,
    mv.f1_score,
    mv.training_data_size,
    mv.created_at,
    mv.status,
    
    -- Performance ranking
    RANK() OVER (PARTITION BY mv.model_type ORDER BY mv.accuracy DESC) as accuracy_rank,
    RANK() OVER (PARTITION BY mv.model_type ORDER BY mv.f1_score DESC) as f1_rank,
    
    -- Training job info
    tj.duration_sec as training_duration,
    tj.final_accuracy as training_final_accuracy
    
FROM model_versions mv
LEFT JOIN training_jobs tj ON mv.id = tj.model_version_id
WHERE mv.status IN ('active', 'validation', 'deprecated')
ORDER BY mv.model_type, mv.accuracy DESC;

-- View for training pipeline status
CREATE OR REPLACE VIEW training_pipeline_status AS
SELECT 
    tj.id as job_id,
    tj.job_name,
    tj.status,
    tj.progress_percent,
    tj.current_step,
    tj.started_at,
    tj.duration_sec,
    
    mv.version as target_version,
    mv.model_type,
    
    -- Progress indicators
    CASE 
        WHEN tj.status = 'completed' THEN 100
        WHEN tj.status = 'failed' THEN -1
        ELSE tj.progress_percent
    END as display_progress,
    
    -- ETA calculation (simplified)
    CASE 
        WHEN tj.status = 'running' AND tj.progress_percent > 0 
        THEN EXTRACT(EPOCH FROM NOW() - tj.started_at) / tj.progress_percent * (100 - tj.progress_percent)
        ELSE NULL
    END as estimated_remaining_sec
    
FROM training_jobs tj
JOIN model_versions mv ON tj.model_version_id = mv.id
WHERE tj.created_at >= NOW() - INTERVAL '7 days'
ORDER BY tj.created_at DESC;

-- Functions for model management
CREATE OR REPLACE FUNCTION activate_model_version(p_version_id UUID) RETURNS BOOLEAN AS $$
DECLARE
    model_type_name VARCHAR(100);
BEGIN
    -- Get model type
    SELECT model_type INTO model_type_name 
    FROM model_versions 
    WHERE id = p_version_id AND status = 'validation';
    
    IF model_type_name IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Deactivate current active model of same type
    UPDATE model_versions 
    SET active = FALSE, deprecated_at = NOW()
    WHERE model_type = model_type_name AND active = TRUE;
    
    -- Activate new model
    UPDATE model_versions 
    SET active = TRUE, status = 'active', activated_at = NOW()
    WHERE id = p_version_id;
    
    -- Record deployment
    INSERT INTO model_deployments (model_version_id, deployment_status, deployed_by)
    VALUES (p_version_id, 'active', 'system');
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to record model performance
CREATE OR REPLACE FUNCTION record_model_performance(
    p_model_version_id UUID,
    p_accuracy DECIMAL,
    p_precision DECIMAL,
    p_recall DECIMAL,
    p_f1 DECIMAL,
    p_total_predictions INTEGER DEFAULT 0,
    p_correct_predictions INTEGER DEFAULT 0
) RETURNS UUID AS $$
DECLARE
    performance_id UUID;
BEGIN
    INSERT INTO model_performance_history (
        model_version_id, accuracy, precision_score, recall_score, f1_score,
        total_predictions, correct_predictions,
        false_positives, false_negatives
    ) VALUES (
        p_model_version_id, p_accuracy, p_precision, p_recall, p_f1,
        p_total_predictions, p_correct_predictions,
        p_total_predictions - p_correct_predictions, -- Simplified FP calculation
        GREATEST(0, p_correct_predictions - p_total_predictions) -- Simplified FN calculation
    ) RETURNING id INTO performance_id;
    
    RETURN performance_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Insert initial model version (from C.1)
INSERT INTO model_versions (
    version, model_type, accuracy, precision_score, recall_score, f1_score,
    training_data_size, model_path, status, active, created_by
) VALUES (
    'v1.0', 'predictive_failure', 0.7500, 0.7200, 0.7800, 0.7500,
    1000, '/models/predictive_v1.0.pkl', 'active', TRUE, 'system'
) ON CONFLICT (version) DO NOTHING;

COMMENT ON TABLE model_versions IS 'Model version management with performance tracking';
COMMENT ON TABLE training_jobs IS 'Automated model training job tracking';
COMMENT ON TABLE model_performance_history IS 'Historical model performance metrics';
COMMENT ON TABLE model_deployments IS 'Model deployment and rollback history';
COMMENT ON FUNCTION activate_model_version IS 'Safely activate a new model version';
COMMENT ON FUNCTION record_model_performance IS 'Record model performance metrics over time';