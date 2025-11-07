# L.5 Cognitive Federation Scaling Design

## Architecture

L.5 implements cognitive federation scaling with 5 core services:

- **l5-orchestrator**: Manages global rollouts and canary deployments
- **l5-model-aggregator**: Federated learning aggregation across regions
- **l5-distiller**: Model compression and knowledge distillation
- **l5-policy-rollout**: Policy deployment with P36 safety controls
- **l5-edge-adapter**: Edge node synchronization and management

## Safety Controls (P36)

- **Approval Gates**: APPROVE_L5_DEPLOY=yes required for live deployments
- **Automatic Rollback**: Health regression triggers automatic rollback
- **Rate Limiting**: Global rollouts are rate-limited to prevent cascades
- **Multi-role Signoffs**: Recorded in reports/l5/approval_signoffs.json

## Operator Runbooks

### Emergency Rollback
```bash
SIMULATION_MODE=false bash infra/scripts/l5/rollback.sh
```

### Health Check
```bash
curl http://localhost:9200/health
curl http://localhost:9201/health
curl http://localhost:9202/health
curl http://localhost:9203/health
curl http://localhost:9204/health
```

### Policy Deployment
```bash
APPROVE_L5_DEPLOY=yes SIMULATION_MODE=false \
  curl -X POST http://localhost:9203/v1/policy/deploy \
  -H "Content-Type: application/json" \
  -d '{"policy":"production-policy"}'
```