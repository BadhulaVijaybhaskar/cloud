-- Migration 003: Create predictions table for predictive intelligence
-- Phase C.1 - Predictive Intelligence Engine

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(255),
    signal_id VARCHAR(255),
    model_version VARCHAR(50) NOT NULL DEFAULT 'v1.0',
    probability DECIMAL(5,4) NOT NULL CHECK (probability >= 0 AND probability <= 1),
    recommendation JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_predictions_run_id (run_id),
    INDEX idx_predictions_signal_id (signal_id),
    INDEX idx_predictions_created_at (created_at DESC)
);

-- Add comments for documentation
COMMENT ON TABLE predictions IS 'Stores ML predictions for failure probability and recommendations';
COMMENT ON COLUMN predictions.probability IS 'Failure probability between 0.0 and 1.0';
COMMENT ON COLUMN predictions.recommendation IS 'JSON object with recommended actions and RCA';
COMMENT ON COLUMN predictions.model_version IS 'Version of the ML model used for prediction';