# K.2 Launch Checklist

## Pre-Launch
- [ ] Security review complete
- [ ] Vault policies configured
- [ ] Model files present in `models/`
- [ ] Terraform plan reviewed
- [ ] Helm charts validated
- [ ] On-call roster confirmed

## 1. Staging Validation
- [ ] Run: `SIMULATION_MODE=true infra/scripts/k2/precheck.sh`
- [ ] Save: `reports/k2/precheck_report.json`
- [ ] Confirm overall_status == PASS

## 2. Approval Gates
- [ ] Security Admin sign-off
- [ ] Ops Lead approval
- [ ] Governance Owner approval
- [ ] Save approvals to `reports/k2/approval_signoffs.json`

## 3. Live Precheck
- [ ] Run: `SIMULATION_MODE=false infra/scripts/k2/precheck.sh`
- [ ] Save: `reports/k2/precheck_report_live.json`
- [ ] Confirm overall_status == PASS

## 4. Canary Deploy
- [ ] Run: `SIMULATION_MODE=false APPROVE_AUTONOMY=yes infra/scripts/k2/deploy.sh`
- [ ] Save: `reports/k2/live_deploy_summary.json`
- [ ] Save: `reports/k2/live_verification_summary.json`

## 5. Observation Window
- [ ] Monitor for 48 hours
- [ ] No critical alerts, no P1-P2 violations
- [ ] Record metrics in `reports/k2/canary_observation.log`

## 6. Rollback (if needed)
- [ ] Run `infra/scripts/k1/deactivate_aol.sh`
- [ ] Run rollback commands
- [ ] Document incident to `reports/k2/postmortem.md`

## 7. Expand Rollout
- [ ] After 48h stable, plan incremental expansion

## Sign-Off
- Security Admin: ___________________  date: _______
- Ops Lead: _________________________ date: _______
- Governance Owner: __________________ date: _______