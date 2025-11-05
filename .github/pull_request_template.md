## Pull request title
Short summary (e.g. feat(k2): add predictive-ops engine and precheck scripts)

## Description
Describe what this PR introduces and which K-phase it addresses.

## Related Tickets / Issues
- Issue: #
- Epics: ATOM-K2

## What changed
- Added: infra/scripts/k2/precheck.sh, infra/scripts/k2/deploy.sh
- Added: infra/terraform/modules/k2_adaptive_ops/...
- Added: reports/k2/* (stubs)

## Evidence / Test Artifacts
Please attach links or paths to generated evidence (CI artifacts or local reports):
- Precheck report (simulation): `reports/k2/precheck_report.json`
- Deploy summary (simulation): `reports/k2/deploy_summary.json`
- Verification summary: `reports/k2/verification_summary.json`
- Coverage / Test artifacts: `reports/k2/test_coverage.json`

If you ran the makefile locally, paste outputs:
```
make k2-precheck
make k2-deploy SIM=true
make k2-verify
```

## Checklist (required before merge)
- [ ] `reports/k2/precheck_report.json` exists and valid JSON
- [ ] `reports/k2/deploy_summary.json` exists and valid JSON
- [ ] `infra/helm/k2-adaptive-ops/` present with Chart.yaml
- [ ] `infra/terraform/modules/k2_adaptive_ops/` present
- [ ] Vault policies updated under `infra/vault/policies/k2_adaptive_ops.hcl`
- [ ] RBAC / namespace scaffolding present under `infra/terraform/...` or `infra/scripts/k2/create_canary_namespace.sh`
- [ ] CI workflow for K.2 present and passing (`.github/workflows/k2_adaptive_ops.yml`)
- [ ] SIMULATION_MODE safe defaults remain in deploy scripts

## Approvals required
- Security Admin
- Ops Lead
- Governance Owner

## Deployment notes
- For live deployment run: `SIMULATION_MODE=false APPROVE_AUTONOMY=yes make k2-deploy`
- Observation window: 48 hours