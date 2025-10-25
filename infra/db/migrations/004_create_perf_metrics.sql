-- Migration 004: Create Performance Metrics Table
-- Phase C.2 - Performance Profiler
-- Stores service latency and throughput benchmarks

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Performance metrics table
CREATE TABLE IF NOT EXISTS perf_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service VARCHAR(100) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    p95_ms DECIMAL(10,2) NOT NULL CHECK (p95_ms >= 0),
    throughput DECIMAL(10,2) NOT NULL CHECK (throughput >= 0),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional metrics
    p50_ms DECIMAL(10,2),
    p99_ms DECIMAL(10,2),
    error_rate DECIMAL(5,2) CHECK (error_rate >= 0 AND error_rate <= 100),
    
    -- Metadata
    test_duration_sec INTEGER DEFAULT 30,
    concurrent_users INTEGER DEFAULT 10,
    
    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_percentiles CHECK (p50_ms <= p95_ms AND p95_ms <= p99_ms)
);

-- Indexes for performance
CREATE INDEX idx_perf_metrics_service ON perf_metrics(service);
CREATE INDEX idx_perf_metrics_timestamp ON perf_metrics(timestamp DESC);
CREATE INDEX idx_perf_metrics_p95 ON perf_metrics(p95_ms);

-- View for latest metrics per service
CREATE OR REPLACE VIEW latest_perf_metrics AS
SELECT DISTINCT ON (service, endpoint) 
    service,
    endpoint,
    p95_ms,
    throughput,
    error_rate,
    timestamp
FROM perf_metrics 
ORDER BY service, endpoint, timestamp DESC;

-- Performance budget alerts (P-6 Policy)
CREATE OR REPLACE VIEW perf_budget_violations AS
SELECT 
    service,
    endpoint,
    p95_ms,
    timestamp,
    (p95_ms - 800.0) as budget_violation_ms
FROM perf_metrics 
WHERE p95_ms > 800.0
ORDER BY timestamp DESC;

COMMENT ON TABLE perf_metrics IS 'Performance profiling results for service endpoints';
COMMENT ON VIEW perf_budget_violations IS 'Services violating P-6 performance budget (p95 > 800ms)';