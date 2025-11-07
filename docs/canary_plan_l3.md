# Canary Plan — L.3 Global Autonomy Exchange

## Purpose
Controlled progressive rollout of L.3 to production with safety gates.

## Preconditions
- `reports/l3/approval_signoffs.json` contains approvals from Security, Ops, Governance (required).
- Vault secrets provisioned (infra/scripts/l3/provision_secrets.sh run with SIM=false).
- mTLS certs validated (infra/scripts/l3/mtls_validate.sh passed).
- Monitoring and alerting active and tested.

## Canary Target
- Namespace: `l3-canary`
- Node group: 2 nodes (isolated)
- Traffic routing: 1% of control-plane traffic for first 24 hours; escalate to 10% at 48h; full at 7 days if stable.

## Steps
1. Create canary namespace and RBAC: `infra/scripts/l3/create_canary_namespace.sh`
2. Deploy L.3 into `l3-canary` with `SIMULATION_MODE=false` and `APPROVE_L3_DEPLOY=yes`
3. Monitor:
   - Prometheus: error rates, latency, policy violations
   - Audit events: check `l3-auditor` for unusual actions
4. Observation window (initial): 48 hours
   - If more than 3 P1 alerts, rollback
   - If any governance violation (P25-P31), rollback immediately
5. Escalation: ops lead + governance owner notified automatically
6. Gradual ramp:
   - Day 1: 1% traffic
   - Day 3: 10% traffic
   - Day 7: 50% traffic
   - Day 14: 100% (if no incidents)
7. Rollback steps:
   - Run `infra/scripts/l3/rollback_canary.sh` which restores previous deployment and revokes canary tokens

## Acceptance Criteria
- 99.95% success rate for canary traffic
- No governance violations logged
- Alert rate below threshold (configurable) for 48h
- Performance within SLOs