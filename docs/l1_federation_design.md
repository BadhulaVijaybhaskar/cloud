# L.1 Federated Autonomy Framework Design Document

## Overview

Phase L.1 implements a secure, policy-controlled Federated Autonomy Framework that enables multiple ATOM Cloud regions, tenants, and edge clusters to coordinate autonomous agents, share non-sensitive knowledge, and perform cross-region collaborative actions while preserving data sovereignty, latency SLAs, and governance.

## Architecture

### Core Services

1. **Federation Orchestrator** (Port 8900)
   - Coordinates federation topology and maintains node registry
   - Manages heartbeat and cross-region action proposals
   - Routes proposals to policy broker for validation

2. **Federation Gateway** (Port 8901)
   - Secure API ingress/egress for federated traffic
   - Handles TLS/mTLS and secure tunnel management
   - Enforces P25 encryption and anonymization requirements

3. **Federation Metadata Store** (Port 8902)
   - Stores sanitized metadata, shared model pointers, and opt-in records
   - Validates metadata against schema requirements
   - Maintains compliance with P25 data sovereignty

4. **Federation Policy Broker** (Port 8903)
   - Validates every federated action against P25-P27 and P1-P24 policies
   - Issues short-lived delegation tokens via Vault
   - Maintains audit trail of policy evaluations

5. **Federation Mirror Agent** (Port 8904)
   - Mirrors approved sanitized artifacts across regions
   - Reconciles local caches and performs sync operations
   - Ensures P25 compliance (no raw tenant data)

## Environment Variables

- `SIMULATION_MODE=true` - Enforce simulation mode for safety
- `APPROVE_FEDERATION=false` - Require explicit approval for live federation
- `VAULT_ADDR=https://vault.atom.internal` - Vault server address
- `NAMESPACE=atom-federation` - Kubernetes namespace
- `FEDERATION_HEARTBEAT_SEC=30` - Node heartbeat interval
- `METADATA_SYNC_INTERVAL_SEC=300` - Metadata sync frequency
- `OPT_IN_EXPIRY_DAYS=365` - Opt-in record expiration

## Reports Generated

- `reports/l1/precheck_report.json` - Environment validation results
- `reports/l1/deploy_summary.json` - Deployment status and artifacts
- `reports/l1/verification_summary.json` - Post-deployment verification
- `reports/l1/federation_health.json` - Federation topology health status

## Governance Policies

### P25 - Federation Data Sovereignty
- Raw tenant data never crosses region boundaries unless explicitly anonymized
- Only metadata, sanitized experience bundles, or derived models may be shared
- Enforced by Federation Policy Broker and Metadata Store

### P26 - Cross-Tenant Opt-In & Consent
- Federation requires active opt-in per tenant/workspace
- Opt-in records are immutable and auditable
- Opt-out propagation enforced system-wide within 30 minutes

### P27 - Federated RBAC & Isolation
- Federation operations require scoped short-lived tokens
- Cross-region actions approved by local RBAC owners
- Delegation tokens managed through Vault dynamic secrets

Defined in `infra/vault/policies/l1_federation.hcl`

## API Endpoints

### Federation Orchestrator
- `POST /v1/register-node` - Register federation node with metadata
- `GET /v1/nodes` - List registered nodes and health status
- `POST /v1/propose-action` - Propose cross-region action
- `GET /v1/proposals/{id}` - Get proposal status and artifacts

### Federation Gateway
- `POST /v1/proxy/{node_id}` - Forward requests through secure tunnel
- `GET /v1/tunnels` - List active tunnels
- `POST /v1/tunnel/{id}/close` - Close active tunnel

### Federation Metadata Store
- `POST /v1/metadata` - Store sanitized shared metadata
- `GET /v1/metadata/{key}` - Retrieve metadata by key
- `GET /v1/metadata` - List all metadata keys
- `DELETE /v1/metadata/{key}` - Delete metadata with audit trail

### Federation Policy Broker
- `POST /v1/validate` - Validate cross-region action against policies
- `POST /v1/delegate` - Request short-lived delegation token
- `GET /v1/validations` - List recent policy validations

### Federation Mirror Agent
- `POST /v1/sync` - Trigger mirror sync job
- `GET /v1/sync-status/{job_id}` - Get sync job status
- `GET /v1/cache/status` - Get local cache status
- `POST /v1/cache/clear` - Clear local mirror cache

## Data Flow

1. **Node Registration**: Regions register with Federation Orchestrator
2. **Opt-In Management**: Tenants provide explicit consent for federation
3. **Action Proposal**: Cross-region actions proposed through Orchestrator
4. **Policy Validation**: Policy Broker validates against P25-P27 and P1-P24
5. **Secure Tunneling**: Gateway establishes encrypted connections
6. **Metadata Sharing**: Sanitized metadata shared through Metadata Store
7. **Artifact Mirroring**: Mirror Agent syncs approved artifacts
8. **Audit Logging**: All actions logged for compliance and governance

## Safety Mechanisms

### Simulation Mode
- All services default to `SIMULATION_MODE=true`
- No live federation actions without explicit approval
- Synthetic data used for testing and validation

### Approval Gates
- `APPROVE_FEDERATION=yes` required for live federation actions
- Legal and data-governance signoffs required
- Explicit stakeholder approval in `reports/l1/approval_signoffs.json`

### Policy Enforcement
- All cross-region actions validated by Policy Broker
- P25-P27 compliance enforced at service level
- Immutable audit trail for regulatory compliance

## Deployment

### Prerequisites
- Kubernetes cluster with RBAC enabled
- Vault for secrets and dynamic token management
- Persistent storage for audit logs and metadata
- Legal approvals for cross-region data sharing

### Configuration
```yaml
global:
  simulationMode: true
  approveFederation: false
  namespace: atom-federation
```

### Scripts
- `infra/scripts/l1/precheck.sh` - Validate federation environment
- `infra/scripts/l1/deploy.sh` - Deploy services (simulation)
- `infra/scripts/l1/verify.sh` - Verify federation deployment

## Security Considerations

- All secrets stored in Vault with P25-P27 policies
- mTLS encryption for all cross-region communication
- Network segmentation between federation services
- Regular security scans of federated actions
- Audit logs protected from tampering

## Compliance

- Maintains immutable opt-in records for regulatory requirements
- Policy validation audit trail for governance
- Data sovereignty enforcement through P25
- Regular compliance reporting capabilities
- Legal approval gates for live federation

## Monitoring and Observability

### Metrics
- Node registration and health status
- Cross-region action success/failure rates
- Policy validation results and violations
- Metadata sync performance and errors
- Tunnel establishment and security metrics

### Alerts
- Policy violations requiring immediate attention
- Node connectivity issues or heartbeat failures
- Unauthorized cross-region access attempts
- Opt-out propagation delays
- Security tunnel establishment failures