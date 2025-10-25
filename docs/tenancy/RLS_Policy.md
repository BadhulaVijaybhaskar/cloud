# Row Level Security (RLS) Policy

## Overview
Multi-tenant data isolation using PostgreSQL RLS policies.

## Implementation
Each table includes `tenant_id` column with RLS policies enforcing tenant isolation.

## Usage
```sql
-- Set tenant context
SET app.current_tenant = 'tenant-123';

-- All queries automatically filtered by tenant
SELECT * FROM workflow_runs; -- Only returns tenant-123 data
```

## JWT Integration
JWT claims mapped to tenant context:
- `sub` claim → user identification  
- `tenant` claim → tenant_id
- `roles` claim → authorization

## Testing RLS
```sql
-- Create test role
CREATE ROLE tenant_user;

-- Test tenant isolation
SET ROLE tenant_user;
SET app.current_tenant = 'tenant-a';
SELECT * FROM workflow_runs; -- Only tenant-a data visible
```