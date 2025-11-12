# Launch Day Runbook — ATOM Cloud (Canonical)

## Overview
Purpose: Controlled production cutover and canary rollout of ATOM Cloud core platform.

**Simulation mode default**: SIMULATION_MODE=true. Change to false only after all approvals.

## Pre-Launch checklist (must be completed)
- [ ] All approvals in `reports/product_approval_bundle.json`.
- [ ] Final security scan OK (no criticals).
- [ ] Billing reconciliation test pass for K.8.
- [ ] On-call roster confirmed (`docs/on_call_roster.md`).
- [ ] PagerDuty/Slack channels configured.
- [ ] Backups & snapshots created (DB + critical state).
- [ ] Approve release: set `APPROVE_DEPLOY=yes` and record in approvals.

## Roles & Contacts
- Release Lead: @release_lead
- Ops Lead: @ops_lead
- Security Admin: @security_admin
- Finance Owner: @finance_owner
- On-call SRE: refer to docs/on_call_roster.md

## Launch sequence (operator commands)
1. Tag release and create release notes.
2. Final precheck (live, staging cluster):
```bash
SIMULATION_MODE=false ./infra/scripts/k8/precheck.sh | tee reports/launch/precheck_live.log
```

3. If precheck passes, run infra apply for target namespace (operator only):

```bash
SIMULATION_MODE=false APPROVE_DEPLOY=yes ./infra/scripts/j5/run_launch_day.sh --stage canary
```

4. Deploy application services (canary namespace):

```bash
SIMULATION_MODE=false ./infra/scripts/k1/activate_aol.sh --namespace atom-canary
SIMULATION_MODE=false ./infra/scripts/k2/deploy.sh --namespace atom-canary
# ... other phase scripts as needed
```

5. Run verification:

```bash
SIMULATION_MODE=false ./infra/scripts/k1/verify_autonomy.sh | tee reports/launch/verify_canary.log
```

6. Open monitoring dashboards (Grafana) and observe for 48h. Execute scripted checks every 5m:

```bash
nohup ./infra/scripts/k1/schedule_verify.sh > reports/launch/schedule.out 2>&1 &
```

## Rollback procedure (immediate)

If any critical alert triggers or governance violation:

```bash
# emergency stop autonomous actions
SIMULATION_MODE=false ./infra/scripts/k1/deactivate_aol.sh

# rollback deployments (example)
kubectl -n atom-canary rollout undo deploy/<svc-name>

# run post-rollback verification
SIMULATION_MODE=false ./infra/scripts/k1/verify_autonomy.sh | tee reports/launch/post_rollback_verify.log
```

## Monitoring during canary (48-hour window)

* Key dashboards: Autonomy Decisions, Policy Violations, Billing Events, Latency/Errors.
* Watchlist alerts:

  * PolicyViolationCritical
  * AutonomyActionErrorRate > 1% sustained 5m
  * Billing Reconciliation deviation > 2%

## Approval to promote to global

Required: Security Admin, Ops Lead, Finance Owner, Governance Owner sign-off documented in `reports/product_approval_bundle.json`.

## Post-launch

* Run full integration tests.
* Archive reports to S3:

```bash
SIMULATION_MODE=false S3_BUCKET=atom-audit-archive ./infra/scripts/l3/archive_reports_to_s3.sh
```

* Schedule review at 72h post-deploy.