# Approval Workflow Policy

## Orchestration Stages

1. **Suggest** - Create incident with recommendations
2. **Dry-Run** - Validate playbook safety
3. **Approve** - Require org-admin approval with justification
4. **Execute** - Run approved playbook with audit logging

## Approval Requirements

- Valid JWT token with `org-admin` role
- Explicit approver ID and justification
- Dry-run must pass before approval
- Complete audit trail for all stages

## Implementation

Orchestrator enforces approval workflow through stage validation and comprehensive audit logging.