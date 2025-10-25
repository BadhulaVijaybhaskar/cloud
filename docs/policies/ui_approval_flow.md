# UI Approval Flow Policy

## Overview
Defines the approval workflow requirements and implementation for the NeuralOps UI.

## Approval Payload Requirements

### Minimum Required Fields
```json
{
  "orchestration_id": "string (required)",
  "approver_id": "string (required)", 
  "justification": "string (required, min 10 chars)",
  "timestamp": "ISO 8601 timestamp (auto-generated)"
}
```

### Validation Rules
- **orchestration_id**: Must reference existing orchestration
- **approver_id**: Must match JWT user_id claim
- **justification**: Minimum 10 characters, maximum 500 characters
- **timestamp**: Auto-generated server-side for audit integrity

## UI Enforcement

### Authorization Requirements
- **Approval Action**: Requires JWT with `org-admin` role
- **Execution Action**: Requires JWT with `execute:playbook` scope
- **View Actions**: Requires valid JWT (any role)

### Workflow Stages
1. **Suggest**: Available to all authenticated users
2. **Dry-Run**: Available to operators and admins
3. **Approve**: Restricted to org-admin role only
4. **Execute**: Restricted to org-admin role only

## Audit Trail Integration

### Retention Policy
- **UI Actions**: Logged to browser console and server
- **Backend Actions**: Stored in orchestrator audit trail
- **S3 Archive**: Daily upload with SHA-256 verification
- **Retention Period**: 90 days minimum

### Audit Linkage
- Each approval generates unique audit entry
- S3 path pattern: `audit/{tenant_id}/{year}/{month}/{day}/{orchestration_id}.json`
- SHA-256 hash included for integrity verification
- Immutable once written

## Security Requirements

### JWT Validation
- All approval actions must validate JWT server-side
- UI must not rely on client-side role checking
- Token expiration must be enforced
- Invalid tokens result in 401 Unauthorized

### CSRF Protection
- SameSite cookies for session management
- CSRF tokens for state-changing operations
- Origin validation for API requests

### Input Sanitization
- All user inputs sanitized before display
- XSS prevention for justification text
- SQL injection prevention (parameterized queries)

## Error Handling

### Approval Failures
- Network errors: Retry with exponential backoff
- Authorization errors: Redirect to login
- Validation errors: Display specific field errors
- Server errors: Generic error message (no sensitive info)

### Audit Failures
- Continue operation but log warning
- Attempt retry for audit logging
- Alert administrators of audit system issues

## Implementation Checklist

### UI Components
- ✅ ApproveModal with justification field
- ✅ JWT token validation
- ✅ Role-based button visibility
- ✅ Error handling and user feedback
- ✅ Audit trail display

### Backend Integration
- ✅ POST /orchestrations/{id}/approve endpoint
- ✅ JWT validation middleware
- ✅ Approval payload validation
- ✅ Audit logging with SHA-256 hash
- ✅ S3 upload for compliance

### Security Measures
- ✅ HTTPS enforcement in production
- ✅ CORS configuration
- ✅ Input sanitization
- ✅ Error message sanitization
- ✅ Rate limiting for approval endpoints