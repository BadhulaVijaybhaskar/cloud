# L.6 Cognitive Resilience & Adaptive Self-Healing Federation Design

## Architecture

L.6 implements cognitive resilience and adaptive self-healing with 5 core services:

- **l6-orchestrator**: Central coordination with P37 safety controls
- **l6-resilience-engine**: Analysis and healing recommendations
- **l6-edge-agent**: Distributed metrics collection and action execution
- **l6-policy-broker**: P37/P38 policy enforcement and evaluation
- **l6-audit-store**: Immutable audit trail for all actions

## Safety Controls

### P37 - Resilience Safety
- Limits concurrent global actions to prevent cascading failures
- Requires APPROVE_L6_DEPLOY=yes for live deployments
- Post-action verification window with auto-rollback triggers

### P38 - Cross-Region Action TTL
- Time-boxed actions with automatic expiration
- Prevents long-running operations from causing drift
- Regional action coordination with TTL enforcement

## Operator Runbooks

### Emergency Rollback
```bash
SIMULATION_MODE=false bash infra/scripts/l6/rollback.sh
```

### Health Check All Services
```bash
curl http://localhost:9200/health  # orchestrator
curl http://localhost:9201/health  # resilience-engine
curl http://localhost:9202/health  # edge-agent
curl http://localhost:9203/health  # policy-broker
curl http://localhost:9204/health  # audit-store
```

### Policy Evaluation Test
```bash
curl -X POST http://localhost:9203/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{"action_type":"scale_up","target":"web-service"}'
```

### Trigger Self-Healing
```bash
curl -X POST http://localhost:9201/v1/heal \
  -H "Content-Type: application/json" \
  -d '{"target":"failing-service","issue":"high_error_rate"}'
```