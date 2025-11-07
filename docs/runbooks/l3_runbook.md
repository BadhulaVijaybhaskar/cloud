# L.3 Global Autonomy Exchange Runbook

## Deployment Steps

1. **Precheck**: Run `SIMULATION_MODE=true bash infra/scripts/l3_gae/precheck.sh`
2. **mTLS Bootstrap**: Run `bash infra/security/mtls_bootstrap.sh`
3. **Deploy**: Run `SIMULATION_MODE=true bash infra/scripts/l3_gae/deploy.sh`
4. **Verify**: Check all services are healthy

## Live Deployment

**CRITICAL**: Requires `APPROVE_L3_DEPLOY=yes` and stakeholder signoffs

1. Security Admin signoff
2. Governance Owner signoff  
3. Legal signoff (cross-region data)
4. Ops Lead signoff
5. Business Owner signoff

## Rollback Procedure

1. Set `SIMULATION_MODE=true`
2. Scale down deployments
3. Restore from backup if needed

## Monitoring

- Check Grafana dashboard: L3 Global Autonomy Exchange
- Monitor proposal processing rate
- Verify mTLS handshake success rate