-- Migration 006: Create Analytics Views and Reports
-- Phase C.4 - Advanced Analytics & Reports
-- Aggregated insights, MTTR, cost metrics, and usage analytics

-- Create analytics summary view
CREATE OR REPLACE VIEW analytics_overview AS
SELECT 
    wr.tenant_id,
    t.name as tenant_name,
    COUNT(DISTINCT wr.id) as total_workflows,
    COUNT(DISTINCT CASE WHEN wr.status = 'failed' THEN wr.id END) as failed_workflows,
    COUNT(DISTINCT CASE WHEN wr.status = 'success' THEN wr.id END) as successful_workflows,
    ROUND(
        COUNT(CASE WHEN wr.status = 'failed' THEN 1 END)::numeric / 
        NULLIF(COUNT(wr.id), 0) * 100, 2
    ) as failure_rate_percent,
    
    -- Performance metrics
    AVG(pm.p95_ms) as avg_p95_latency_ms,
    AVG(pm.throughput) as avg_throughput_rps,
    
    -- Prediction metrics
    COUNT(DISTINCT p.id) as total_predictions,
    AVG(p.probability) as avg_failure_probability,
    
    -- Time ranges
    MIN(wr.created_at) as first_workflow,
    MAX(wr.created_at) as last_workflow,
    
    -- Current period (last 30 days)
    COUNT(DISTINCT CASE 
        WHEN wr.created_at >= NOW() - INTERVAL '30 days' 
        THEN wr.id 
    END) as workflows_last_30d
    
FROM workflow_runs wr
LEFT JOIN tenants t ON wr.tenant_id = t.id
LEFT JOIN perf_metrics pm ON pm.tenant_id = wr.tenant_id
LEFT JOIN predictions p ON p.tenant_id = wr.tenant_id
WHERE t.active = true
GROUP BY wr.tenant_id, t.name;

-- Create MTTR (Mean Time To Recovery) view
CREATE OR REPLACE VIEW mttr_analysis AS
WITH incident_recovery AS (
    SELECT 
        wr.tenant_id,
        wr.id as workflow_id,
        wr.created_at as incident_start,
        
        -- Find next successful run after failure
        LEAD(wr.created_at) OVER (
            PARTITION BY wr.tenant_id, wr.workflow_name 
            ORDER BY wr.created_at
        ) as recovery_time,
        
        -- Calculate recovery duration
        EXTRACT(EPOCH FROM (
            LEAD(wr.created_at) OVER (
                PARTITION BY wr.tenant_id, wr.workflow_name 
                ORDER BY wr.created_at
            ) - wr.created_at
        )) / 60 as recovery_minutes
        
    FROM workflow_runs wr
    WHERE wr.status = 'failed'
)
SELECT 
    ir.tenant_id,
    t.name as tenant_name,
    COUNT(*) as total_incidents,
    ROUND(AVG(ir.recovery_minutes), 2) as avg_mttr_minutes,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ir.recovery_minutes), 2) as median_mttr_minutes,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ir.recovery_minutes), 2) as p95_mttr_minutes,
    MIN(ir.recovery_minutes) as min_recovery_minutes,
    MAX(ir.recovery_minutes) as max_recovery_minutes
FROM incident_recovery ir
JOIN tenants t ON ir.tenant_id = t.id
WHERE ir.recovery_time IS NOT NULL
GROUP BY ir.tenant_id, t.name;

-- Create cost analysis view (simulated metrics)
CREATE OR REPLACE VIEW cost_analysis AS
SELECT 
    wr.tenant_id,
    t.name as tenant_name,
    
    -- Compute cost estimates (simulated)
    COUNT(wr.id) * 0.01 as workflow_execution_cost,
    COUNT(DISTINCT pm.id) * 0.005 as monitoring_cost,
    COUNT(DISTINCT p.id) * 0.02 as prediction_cost,
    
    -- Total estimated cost
    (COUNT(wr.id) * 0.01) + 
    (COUNT(DISTINCT pm.id) * 0.005) + 
    (COUNT(DISTINCT p.id) * 0.02) as total_estimated_cost,
    
    -- Usage metrics
    COUNT(wr.id) as total_executions,
    COUNT(DISTINCT wr.workflow_name) as unique_workflows,
    COUNT(DISTINCT pm.service) as monitored_services,
    
    -- Time-based costs
    EXTRACT(EPOCH FROM (MAX(wr.created_at) - MIN(wr.created_at))) / 3600 as usage_hours,
    
    -- Cost per hour
    CASE 
        WHEN EXTRACT(EPOCH FROM (MAX(wr.created_at) - MIN(wr.created_at))) > 0 
        THEN ROUND(
            ((COUNT(wr.id) * 0.01) + (COUNT(DISTINCT pm.id) * 0.005) + (COUNT(DISTINCT p.id) * 0.02)) / 
            (EXTRACT(EPOCH FROM (MAX(wr.created_at) - MIN(wr.created_at))) / 3600), 4
        )
        ELSE 0 
    END as cost_per_hour
    
FROM workflow_runs wr
LEFT JOIN tenants t ON wr.tenant_id = t.id
LEFT JOIN perf_metrics pm ON pm.tenant_id = wr.tenant_id
LEFT JOIN predictions p ON p.tenant_id = wr.tenant_id
WHERE t.active = true
GROUP BY wr.tenant_id, t.name;

-- Create usage trends view
CREATE OR REPLACE VIEW usage_trends AS
SELECT 
    wr.tenant_id,
    t.name as tenant_name,
    DATE_TRUNC('day', wr.created_at) as usage_date,
    
    COUNT(wr.id) as daily_workflows,
    COUNT(CASE WHEN wr.status = 'failed' THEN 1 END) as daily_failures,
    COUNT(CASE WHEN wr.status = 'success' THEN 1 END) as daily_successes,
    
    -- Daily failure rate
    ROUND(
        COUNT(CASE WHEN wr.status = 'failed' THEN 1 END)::numeric / 
        NULLIF(COUNT(wr.id), 0) * 100, 2
    ) as daily_failure_rate,
    
    -- Performance trends
    AVG(pm.p95_ms) as daily_avg_latency,
    AVG(pm.throughput) as daily_avg_throughput
    
FROM workflow_runs wr
LEFT JOIN tenants t ON wr.tenant_id = t.id
LEFT JOIN perf_metrics pm ON pm.tenant_id = wr.tenant_id 
    AND DATE_TRUNC('day', pm.timestamp) = DATE_TRUNC('day', wr.created_at)
WHERE t.active = true
    AND wr.created_at >= NOW() - INTERVAL '90 days'  -- Last 90 days
GROUP BY wr.tenant_id, t.name, DATE_TRUNC('day', wr.created_at)
ORDER BY usage_date DESC;

-- Create service health dashboard view
CREATE OR REPLACE VIEW service_health_dashboard AS
SELECT 
    pm.tenant_id,
    t.name as tenant_name,
    pm.service,
    pm.endpoint,
    
    -- Latest metrics
    MAX(pm.timestamp) as last_check,
    AVG(pm.p95_ms) as avg_latency_ms,
    AVG(pm.throughput) as avg_throughput_rps,
    AVG(pm.error_rate) as avg_error_rate,
    
    -- Health status
    CASE 
        WHEN AVG(pm.p95_ms) > 800 THEN 'CRITICAL'
        WHEN AVG(pm.p95_ms) > 500 THEN 'WARNING'
        WHEN AVG(pm.error_rate) > 5 THEN 'WARNING'
        ELSE 'HEALTHY'
    END as health_status,
    
    -- Trend indicators (last 24h vs previous 24h)
    AVG(CASE 
        WHEN pm.timestamp >= NOW() - INTERVAL '24 hours' 
        THEN pm.p95_ms 
    END) as latency_24h,
    AVG(CASE 
        WHEN pm.timestamp >= NOW() - INTERVAL '48 hours' 
        AND pm.timestamp < NOW() - INTERVAL '24 hours'
        THEN pm.p95_ms 
    END) as latency_prev_24h
    
FROM perf_metrics pm
JOIN tenants t ON pm.tenant_id = t.id
WHERE t.active = true
    AND pm.timestamp >= NOW() - INTERVAL '7 days'  -- Last week
GROUP BY pm.tenant_id, t.name, pm.service, pm.endpoint;

-- Create prediction accuracy view
CREATE OR REPLACE VIEW prediction_accuracy AS
WITH prediction_outcomes AS (
    SELECT 
        p.tenant_id,
        p.id as prediction_id,
        p.probability,
        p.created_at as prediction_time,
        
        -- Check if failure actually occurred within next hour
        EXISTS(
            SELECT 1 FROM workflow_runs wr 
            WHERE wr.tenant_id = p.tenant_id
            AND wr.status = 'failed'
            AND wr.created_at BETWEEN p.created_at AND p.created_at + INTERVAL '1 hour'
        ) as actual_failure,
        
        -- Prediction threshold (>0.5 = predicted failure)
        CASE WHEN p.probability > 0.5 THEN true ELSE false END as predicted_failure
        
    FROM predictions p
    WHERE p.created_at >= NOW() - INTERVAL '30 days'
)
SELECT 
    po.tenant_id,
    t.name as tenant_name,
    COUNT(*) as total_predictions,
    
    -- Accuracy metrics
    COUNT(CASE 
        WHEN po.predicted_failure = po.actual_failure 
        THEN 1 
    END) as correct_predictions,
    
    ROUND(
        COUNT(CASE WHEN po.predicted_failure = po.actual_failure THEN 1 END)::numeric / 
        COUNT(*) * 100, 2
    ) as accuracy_percent,
    
    -- Precision and Recall
    COUNT(CASE 
        WHEN po.predicted_failure = true AND po.actual_failure = true 
        THEN 1 
    END) as true_positives,
    
    COUNT(CASE 
        WHEN po.predicted_failure = true AND po.actual_failure = false 
        THEN 1 
    END) as false_positives,
    
    COUNT(CASE 
        WHEN po.predicted_failure = false AND po.actual_failure = true 
        THEN 1 
    END) as false_negatives,
    
    AVG(po.probability) as avg_prediction_confidence
    
FROM prediction_outcomes po
JOIN tenants t ON po.tenant_id = t.id
GROUP BY po.tenant_id, t.name;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_analytics_tenant_created ON workflow_runs(tenant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_perf_metrics_tenant_timestamp ON perf_metrics(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_predictions_tenant_created ON predictions(tenant_id, created_at);

-- Create materialized view for expensive aggregations (optional)
-- CREATE MATERIALIZED VIEW analytics_summary_materialized AS
-- SELECT * FROM analytics_overview;

COMMENT ON VIEW analytics_overview IS 'High-level analytics dashboard with key metrics per tenant';
COMMENT ON VIEW mttr_analysis IS 'Mean Time To Recovery analysis for incident management';
COMMENT ON VIEW cost_analysis IS 'Cost estimation and usage metrics per tenant';
COMMENT ON VIEW usage_trends IS 'Daily usage trends and patterns over time';
COMMENT ON VIEW service_health_dashboard IS 'Real-time service health monitoring';
COMMENT ON VIEW prediction_accuracy IS 'ML model accuracy and performance metrics';