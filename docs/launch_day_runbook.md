# K.2 Launch Day Runbook (Canary + Expansion)

## Objective
Run a safe canary of K.2 adaptive scaling and predictive ops, validate behavior, and expand if stable.

## Roles
- **On-call Ops**: watches alerts and executes runbook steps
- **Security Admin**: verifies vault & policies pre-launch
- **Governance Owner**: monitors policy logs and signs off
- **SRE Lead**: approves expansion

## Steps — Canary Day
1. Pre-launch: ensure approvals in `reports/k2/approval_signoffs.json`
2. Run live precheck (staging):
   - `SIMULATION_MODE=false infra/scripts/k2/precheck.sh`
   - Save `reports/k2/precheck_report_live.json`
3. If PASS: Run canary deploy:
   - `SIMULATION_MODE=false APPROVE_AUTONOMY=yes infra/scripts/k2/deploy.sh`
   - Save `reports/k2/live_deploy_summary.json`
4. Monitor dashboards continuously. Key metrics:
   - Forecast Accuracy P95
   - Decision latency P95
   - Policy violations
   - Pod restarts & error rate
5. If critical alert:
   - Run `infra/scripts/k1/deactivate_aol.sh`
   - Run `kubectl -n atom-k2-canary rollout undo deploy/<service>`
   - Document incident in `reports/k2/postmortem.md`
6. After 48 hours: compile `reports/k2/canary_observation.log` and sign-off to expand.

## Escalation
- Pager duty → Ops Lead → SRE Lead → Governance Owner

## Rollback safe commands
- `infra/scripts/k1/deactivate_aol.sh`
- `kubectl -n atom-k2-canary rollout undo deploy/<svc>`
- `kubectl -n atom-k2-canary scale deploy <svc> --replicas=1`

## Post-launch
- Create postmortem or success report and place in `reports/k2/`