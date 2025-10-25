-- Migration 002: Create insight_signals table
-- Stores anomaly detection signals from Prometheus metrics

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE insight_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    hint TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX idx_insight_signals_metric ON insight_signals(metric);
CREATE INDEX idx_insight_signals_score ON insight_signals(score DESC);
CREATE INDEX idx_insight_signals_created_at ON insight_signals(created_at DESC);
CREATE INDEX idx_insight_signals_metric_created ON insight_signals(metric, created_at DESC);