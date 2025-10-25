# Safety Policy

**Default:** `safety.mode = manual`

All playbooks require explicit approval for execution.

## Auto-Execution Requirements
- `allowed_roles` includes `org-admin`
- Risk score < 50
- Pre-approved playbooks only

## Implementation
- JWT token validation for approvers
- Comprehensive audit trail logging
- Dry-run validation before execution