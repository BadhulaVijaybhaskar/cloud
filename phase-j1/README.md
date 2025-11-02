# Phase J.1 - Production Launch Operations

## Overview
Phase J.1 bridges the gap between validated simulation environments and live production deployment, providing comprehensive production operations capabilities for ATOM Cloud.

## Architecture

### Core Services (6 microservices)
1. **Deployment Orchestrator** (port 10001) - Production deployment management
2. **Canary Controller** (port 10002) - Live canary deployments with traffic routing
3. **Telemetry Hub** (port 10003) - Production observability and monitoring
4. **Billing Agent** (port 10004) - Cost tracking and governance
5. **Launch Control UI** (port 10005) - Operations dashboard
6. **Ops Gateway** (port 10006) - API aggregation and orchestration

### New Production Policies (P16-P20)
- **P16**: Real Infrastructure Separation
- **P17**: Deployment Verification  
- **P18**: Rollback Readiness
- **P19**: Live Observability
- **P20**: Access & Cost Governance

## Quick Start

### Prerequisites
- Python 3.11+
- Terraform (for infrastructure)
- kubectl (for Kubernetes)
- Helm (for application deployment)

### Environment Variables
```bash
export CLOUD_PROVIDER="gcp"
export REGION="us-central1"
export K8S_CONTEXT="atom-prod-cluster"
export VAULT_ADDR="https://vault.atom-cloud.io"
export PROM_URL="https://prometheus.atom-cloud.io"
export GRAFANA_URL="https://grafana.atom-cloud.io"
export BILLING_KEY="production-billing-key"
export SIMULATION_MODE="false"
```

### Running Services
```bash
# Start all services (separate terminals)
python phase-j1/services/deployment-orchestrator/main.py
python phase-j1/services/canary-controller/main.py
python phase-j1/services/telemetry-hub/main.py
python phase-j1/services/billing-agent/main.py
python phase-j1/services/launch-control-ui/main.py
python phase-j1/services/ops-gateway/main.py
```

### Infrastructure Deployment
```bash
# Deploy infrastructure with Terraform
cd phase-j1/infra/terraform
terraform init
terraform plan
terraform apply

# Deploy applications with Helm
cd ../helm
helm install atom-prod . -f values.yaml
```

## API Endpoints

### Deployment Orchestrator (10001)
- `POST /v1/deploy` - Deploy service to production
- `GET /v1/deployments/{id}` - Get deployment status
- `POST /v1/deployments/{id}/rollback` - Rollback deployment

### Canary Controller (10002)
- `POST /v1/canary/start` - Start canary deployment
- `GET /v1/canary/{id}` - Get canary status and metrics
- `POST /v1/canary/{id}/promote` - Promote canary to production
- `POST /v1/canary/{id}/rollback` - Rollback canary

### Telemetry Hub (10003)
- `POST /v1/metrics` - Ingest metrics from services
- `POST /v1/traces` - Ingest OpenTelemetry traces
- `POST /v1/logs` - Ingest structured logs
- `GET /v1/dashboard` - Get observability dashboard data

### Billing Agent (10004)
- `POST /v1/usage` - Record resource usage
- `POST /v1/budgets` - Create cost budgets
- `GET /v1/costs/{service}` - Get service cost breakdown
- `GET /v1/alerts` - Get cost alerts

### Launch Control UI (10005)
- `GET /` - Main operations dashboard
- `GET /api/v1/deployments` - Get deployment status
- `GET /api/v1/canaries` - Get canary status
- `GET /api/v1/telemetry` - Get system health metrics
- `GET /api/v1/billing` - Get cost overview

### Ops Gateway (10006)
- `GET /v1/status` - Get overall system status
- `POST /v1/deploy` - Proxy deployment requests
- `POST /v1/canary/start` - Proxy canary requests
- `GET /v1/metrics/aggregate` - Get aggregated metrics
- `POST /v1/emergency/stop` - Emergency stop operations

## Production Policies

### P16 - Real Infrastructure Separation
- Sandbox and production environments completely isolated
- No shared data, storage, or compute resources
- Enforced by deployment orchestrator and Vault policies

### P17 - Deployment Verification
- Pre-deploy smoke tests required
- Post-deploy SLO verification
- Automated rollback on verification failure

### P18 - Rollback Readiness
- Pre-verified rollback artifacts
- Automated rollback triggers
- Complete audit trail for all rollbacks

### P19 - Live Observability
- Prometheus metrics from all services
- OpenTelemetry distributed tracing
- Structured JSON logging
- Real-time dashboards and alerting

### P20 - Access & Cost Governance
- Cost telemetry and budget enforcement
- Role-based access control
- Multi-region cost tracking
- Automated cost alerts and limits

## Deployment Workflows

### Standard Deployment
1. Pre-deployment checks and validation
2. Infrastructure provisioning (if needed)
3. Application deployment via Helm
4. Health verification and smoke tests
5. Traffic routing and load balancer updates
6. Post-deployment monitoring

### Canary Deployment
1. Deploy canary version alongside production
2. Route small percentage of traffic to canary
3. Monitor metrics and health indicators
4. Gradually increase traffic if metrics are good
5. Promote to full production or rollback
6. Complete audit and reporting

### Emergency Rollback
1. Detect failure or trigger emergency stop
2. Immediately route traffic away from failed version
3. Rollback to last known good version
4. Verify system health and stability
5. Generate incident report and audit trail

## Monitoring & Observability

### Key Metrics
- **Deployment Success Rate**: Percentage of successful deployments
- **Canary Promotion Rate**: Percentage of canaries promoted to production
- **System Availability**: Overall system uptime and availability
- **Response Latency**: P95 response times across services
- **Error Rates**: Application and infrastructure error rates
- **Cost Metrics**: Daily/monthly spend and budget utilization

### Dashboards
- **Operations Dashboard**: Real-time system status and health
- **Deployment Dashboard**: Deployment history and success rates
- **Cost Dashboard**: Spend tracking and budget monitoring
- **Performance Dashboard**: Latency, throughput, and error metrics

### Alerting
- **Critical Alerts**: System failures, security breaches
- **Warning Alerts**: Performance degradation, budget overruns
- **Info Alerts**: Successful deployments, routine maintenance

## Security & Compliance

### Access Control
- Role-based permissions for all operations
- Multi-factor authentication required
- Audit logging for all administrative actions
- Principle of least privilege enforcement

### Data Protection
- Encryption at rest and in transit
- PII detection and masking
- Secure secret management via Vault
- Regular security audits and penetration testing

### Compliance
- SOC 2 Type II compliance
- GDPR and CCPA data protection
- HIPAA compliance for healthcare workloads
- Regular compliance audits and reporting

## Troubleshooting

### Common Issues
1. **Deployment Failures**: Check pre-deployment validation and resource availability
2. **Canary Issues**: Verify traffic routing and health check configuration
3. **Cost Overruns**: Review resource usage and budget settings
4. **Performance Issues**: Check system metrics and scaling configuration

### Debug Commands
```bash
# Check service health
curl http://localhost:10001/health

# View deployment status
curl http://localhost:10001/v1/deployments

# Check canary metrics
curl http://localhost:10002/v1/canaries

# View system status
curl http://localhost:10006/v1/status
```

## Production Readiness Checklist

- [ ] All environment variables configured
- [ ] Infrastructure provisioned and validated
- [ ] Services deployed and health checks passing
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery tested
- [ ] Security policies implemented and tested
- [ ] Cost budgets and alerts configured
- [ ] Runbooks and documentation complete
- [ ] Team training and access provisioned
- [ ] Go-live approval obtained

## License
Apache 2.0 - See LICENSE file for details