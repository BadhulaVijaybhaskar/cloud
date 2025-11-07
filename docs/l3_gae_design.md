# L.3 — Global Autonomy Exchange (GAE) Design

## Overview
The Global Autonomy Exchange enables secure, policy-compliant cross-region artifact and proposal exchange between autonomous nodes.

## Architecture
- **Orchestrator** (9005): Cross-region coordination
- **Gateway** (9006): mTLS API gateway
- **Metadata Store** (9007): Artifact metadata and policies
- **Exchange Bus** (9008): Message routing
- **Auditor** (9009): Audit trail recording

## Data Contracts
See `infra/contracts/l3_gae/openapi_l3_gae.yaml` for API specifications.

## Policy Requirements
- P25-P31 inheritance from L.2 governance
- Cross-region exchanges must pass policy checks
- All exchanges recorded in auditor

## Runbook
Use SIMULATION_MODE=true by default. See `infra/scripts/l3/` for precheck/deploy/verify.

## Operator Guidance
- Live deploy requires APPROVE_L3_DEPLOY=yes
- mTLS certificates must be configured for cross-region communication
- Monitor audit trail for compliance