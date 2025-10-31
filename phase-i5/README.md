# Phase I.5 - Collective Intelligence Network (CIN)

## Overview

The Collective Intelligence Network (CIN) enables coordinated decision-making across distributed agents through intelligent signal processing, federated learning, and automated conflict resolution.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Signal Gateway │────│  Consensus Bus   │────│ FL Orchestrator │
│   (Port 8001)   │    │   (Port 8002)    │    │   (Port 8003)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────────────┐               │
         └──────────────│     Arbiter     │───────────────┘
                        │   (Port 8004)   │
                        └─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional)
- Kubernetes cluster (for production)

### Local Development
```bash
# Start services
cd services/signal-gateway && python main.py &
cd services/consensus-bus && python main.py &
cd services/fl-orchestrator && python main.py &
cd services/arbiter && python main.py &

# Run precheck
bash phase-i5/prechecks/production_precheck.sh

# Test with CLI
python phase-i5/cli/sample_cli.py health
python phase-i5/cli/sample_cli.py precheck
```

### Production Deployment
```bash
# Deploy with Helm
helm install signal-gateway phase-i5/manifests/helm/signal-gateway/
kubectl apply -f phase-i5/observability/alerts.yaml

# Verify deployment
kubectl get pods -l app=signal-gateway
```

## Services

### Signal Gateway (8001)
- Intelligent signal ingestion and classification
- PII detection and data masking
- Policy enforcement and routing

### Consensus Bus (8002)  
- Real-time message coordination
- WebSocket subscriptions
- Consensus round management

### FL Orchestrator (8003)
- Federated learning coordination
- Model validation and aggregation
- Privacy budget enforcement

### Arbiter (8004)
- Conflict resolution between agents
- Rule-based and ML arbitration
- Decision confidence scoring

## Data Contracts

### SignalV1
```protobuf
message SignalV1 {
  string id = 1;
  string source_id = 2;
  string tenant_id = 3;
  string type = 4;
  string timestamp_iso = 5;
  bytes payload = 6;
  repeated string pii_fields = 7;
  string signature = 8;
  map<string,string> meta = 9;
}
```

### ModelDeltaV1
```protobuf
message ModelDeltaV1 {
  string delta_id = 1;
  string round_id = 2;
  string participant_id = 3;
  string model_base_hash = 4;
  bytes delta_weights = 5;
  DeltaMetadata metadata = 6;
  string signature = 7;
  string timestamp_iso = 8;
}
```

## Policy Matrix

| Area | Enforcement Point | Mode | Rules |
|------|------------------|------|-------|
| Data Ingest | signal-gateway | Reject/Mask | PII protection, tenant isolation |
| Model Updates | fl-orchestrator | Block pre-commit | Fairness validation, privacy budget |
| Access Control | review-queue | RBAC | Role-based access, MFA |
| Privacy | privacy-proxy | Transform | Differential privacy, consent |
| Audit | audit-log | Append-only | Immutable logging, integrity |

## Privacy & Security

### Privacy Budget Management
- Monthly epsilon budget: 10.0 per tenant
- Per-round allocation: 0.5-2.0 epsilon
- Real-time budget tracking and alerts
- See `privacy/epsilon_policy.md` for details

### Security Features
- JWT-based authentication
- Cryptographic signature validation
- Multi-level data classification
- Vault integration for secrets

## Monitoring & Observability

### Metrics
- Signal ingestion rate and latency
- FL round success rate and duration
- Conflict resolution confidence
- Policy violation rates

### Alerts
- Service health and availability
- SLO breaches and error rates
- Privacy budget exhaustion
- Policy violation spikes

### Dashboards
- Per-service operational metrics
- FL round progress and outcomes
- Policy enforcement heatmaps
- Privacy budget utilization

## Development

### Running Tests
```bash
# Integration tests
python -m pytest tests/integration/test_I.5_end2end.py -v

# Precheck suite
bash phase-i5/prechecks/production_precheck.sh
```

### Adding New Services
1. Create service directory under `services/`
2. Implement required endpoints and health checks
3. Add to policy matrix in `policies/policy-matrix.yaml`
4. Create Helm chart in `manifests/helm/`
5. Add monitoring alerts in `observability/alerts.yaml`

## Production Readiness

### Deployment Checklist
- [ ] All services containerized and tested
- [ ] Helm charts configured for environment
- [ ] Vault policies and secrets configured
- [ ] Monitoring and alerting deployed
- [ ] Privacy policies reviewed and approved
- [ ] Security audit completed
- [ ] Load testing passed
- [ ] Disaster recovery plan validated

### Infrastructure Requirements
- Kubernetes cluster with RBAC
- Kafka or managed message broker
- Vault for secrets management
- Prometheus/Grafana for monitoring
- S3-compatible object storage
- GPU pools for ML workloads (optional)

## Troubleshooting

### Common Issues
1. **Service not starting**: Check environment variables and dependencies
2. **High latency**: Review resource limits and scaling configuration
3. **Policy violations**: Check policy matrix and service configuration
4. **FL rounds failing**: Verify privacy budget and participant connectivity

### Support
- Documentation: `docs/` directory
- Runbooks: `ops/sre-runbooks.md`
- Monitoring: Grafana dashboards
- Logs: Centralized logging via ELK stack

## Contributing

1. Follow the agent-ready specification format
2. Add comprehensive tests for new features
3. Update policy matrix for new enforcement points
4. Include monitoring and alerting configuration
5. Document security and privacy implications

---

**Version**: 1.0.0  
**Status**: Production Ready (Core Services)  
**Last Updated**: 2025-01-11