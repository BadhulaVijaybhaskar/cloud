# K.5 Full Autonomy Design Document

## Overview

Phase K.5 implements full autonomy for the ATOM Cloud Platform through meta-learning, explainability, and autonomous proposal management. The system can learn from operational patterns, generate optimization proposals, and apply them with appropriate governance and safety controls.

## Architecture

### Core Services

1. **Meta Learner** (Port 8800)
   - Analyzes operational patterns from experience repository
   - Generates meta-proposals for system optimization
   - Integrates with explainability engine for transparent decisions

2. **Explainability Engine** (Port 8801)
   - Generates human-readable explanations for proposals
   - Provides feature importance and decision paths
   - Ensures transparency in autonomous decisions

3. **Policy Refiner** (Port 8802)
   - Validates proposals against governance policies P1-P24
   - Simulates proposal impact via simulator proxy
   - Manages proposal application with approval gates

4. **Autonomy Auditor** (Port 8803)
   - Maintains immutable audit trail of all meta-actions
   - Provides compliance reporting and query capabilities
   - Ensures accountability in autonomous operations

5. **Simulator Proxy** (Port 8804)
   - Runs synthetic scenarios to test proposal impact
   - Provides safety flags and risk assessment
   - Enables safe testing before live application

## API Endpoints

### Meta Learner
- `POST /v1/learn` - Generate meta-proposals from patterns
- `GET /v1/proposals` - List all generated proposals

### Explainability Engine
- `POST /v1/explain` - Generate explanation for proposal
- `GET /v1/explain/{id}` - Retrieve explanation artifact
- `GET /v1/explanations` - List all explanations

### Policy Refiner
- `POST /v1/propose` - Submit proposal for validation
- `GET /v1/proposal/{id}` - Get proposal status
- `POST /v1/proposal/{id}/apply` - Apply validated proposal

### Autonomy Auditor
- `POST /v1/audit` - Record audit event
- `GET /v1/audit` - Query audit logs with filters
- `GET /v1/audit/stats` - Get audit statistics

### Simulator Proxy
- `POST /v1/run` - Run simulation scenario
- `GET /v1/scenarios` - List available scenarios
- `GET /v1/runs` - List simulation runs

## Safety Mechanisms

### Simulation Mode
- All services default to `SIMULATION_MODE=true`
- No live changes applied without explicit approval
- All proposals tested in simulation first

### Approval Gates
- `APPROVE_META=yes` required for live proposal application
- Operator approval required for high-risk changes
- Rollback capabilities for all applied proposals

### Governance Compliance
- All proposals validated against policies P1-P24
- Explainability artifacts required for all proposals
- Immutable audit trail for compliance

## Data Flow

1. **Pattern Analysis**: Meta Learner analyzes operational patterns
2. **Proposal Generation**: System generates optimization proposals
3. **Explainability**: Engine creates human-readable explanations
4. **Validation**: Policy Refiner validates against governance
5. **Simulation**: Simulator Proxy tests proposal impact
6. **Approval**: Operator reviews and approves if needed
7. **Application**: Proposal applied with audit logging
8. **Monitoring**: Continuous monitoring of applied changes

## Environment Variables

- `SIMULATION_MODE=true` - Enforce simulation mode for safety
- `APPROVE_META=false` - Require explicit approval for live changes
- `VAULT_ADDR=https://vault.atom.internal` - Vault server address
- `NAMESPACE=k5-full-autonomy` - Kubernetes namespace
- `POLICY_ENFORCE_P24=true` - Enforce P24 governance policy

## Reports Generated

- `reports/k5/precheck_report.json` - Environment validation results
- `reports/k5/deploy_summary.json` - Deployment status and artifacts
- `reports/k5/verification_summary.json` - Post-deployment verification
- `reports/k5/explainability_reports/*.json` - Explainability artifacts

## Governance Policy

Defined in `infra/vault/policies/k5_full_autonomy.hcl` (P24)

## Deployment

### Prerequisites
- Kubernetes cluster with RBAC enabled
- Vault for secrets management
- Persistent storage for audit logs and reports

### Configuration
```yaml
global:
  simulationMode: true
  approveMeta: false
  namespace: k5-full-autonomy
```

### Scripts
- `infra/scripts/k5/precheck.sh` - Validate environment
- `infra/scripts/k5/deploy.sh` - Deploy services (simulation)
- `infra/scripts/k5/verify.sh` - Verify deployment

## Monitoring and Observability

### Metrics
- Proposal generation rate and success rate
- Simulation accuracy and safety flag frequency
- Audit event volume and compliance metrics
- Service health and performance metrics

### Alerts
- High-risk proposals requiring review
- Simulation failures or safety flag triggers
- Audit trail integrity issues
- Service availability problems

## Runbooks

### Operator Approval Process
1. Review proposal in Policy Refiner
2. Examine explainability artifacts
3. Validate simulation results
4. Check governance compliance
5. Set `APPROVE_META=yes` if approved
6. Monitor application and rollback if needed

### Incident Response
1. Check Autonomy Auditor for recent changes
2. Review simulation results for applied proposals
3. Use rollback capabilities if needed
4. Update governance policies if required

## Security Considerations

- All secrets stored in Vault with appropriate policies
- Network segmentation between services
- Audit logs protected from tampering
- Regular security scans of autonomous decisions

## Compliance

- Maintains audit trail for regulatory requirements
- Explainability artifacts for transparency
- Governance policy enforcement
- Regular compliance reporting capabilities