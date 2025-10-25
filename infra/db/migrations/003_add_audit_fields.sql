-- Add audit fields to workflow_runs table
ALTER TABLE workflow_runs 
ADD COLUMN approved_by VARCHAR(255),
ADD COLUMN approved_at TIMESTAMP,
ADD COLUMN cosign_sig TEXT,
ADD COLUMN immutable_log_path VARCHAR(500);

-- Create audit_logs table for immutable audit records
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    workflow_run_id UUID REFERENCES workflow_runs(id),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    immutable_hash VARCHAR(64) NOT NULL UNIQUE
);

-- Create index for efficient queries
CREATE INDEX idx_audit_logs_workflow_run_id ON audit_logs(workflow_run_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);