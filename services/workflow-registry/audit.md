# ATOM Audit Logging

## Overview
Immutable audit logging for workflow executions with object storage integration.

## Audit Fields
- `approved_by`: User who approved the workflow execution
- `approved_at`: Timestamp of approval
- `cosign_sig`: Cosign signature verification result
- `immutable_log_path`: S3/MinIO path to immutable audit record

## Audit Events
- `workflow_registered`: WPK package uploaded
- `workflow_approved`: Manual approval granted
- `workflow_executed`: Workflow execution started
- `workflow_completed`: Workflow execution finished
- `workflow_failed`: Workflow execution failed

## Implementation
Audit records are generated as JSON and uploaded to object storage with SHA-256 hash verification for immutability.