# Release: ATOM Cloud — K/L Series Bundle

## Summary
This PR packages simulation artifacts and evidence for the full K/L product rollout candidate.

**Includes:** reports/* JSON artifacts for K1..K9, L1..L7 (precheck, deploy, verification), approval_signoffs.json, runbooks.

## Evidence files attached
- reports/k1/*
- reports/k2/*
- reports/k3/*
- reports/k4/*
- reports/k5/*
- reports/k6/*
- reports/k7/*
- reports/k8/*
- reports/k9/*
- reports/l1/*
- reports/l2/*
- reports/l3/*
- reports/l4/*
- reports/l5/*
- reports/l6/*
- reports/l7/*
- reports/product_approval_bundle.json

## Checklist (required before merge)
- [ ] Legal signoff attached (`reports/*/approval_signoffs.json`)
- [ ] Security signoff attached
- [ ] Finance signoff attached
- [ ] Ops signoff attached
- [ ] On-call roster attached (`docs/on_call_roster.md`)
- [ ] Launch runbook attached (`docs/launch_day_runbook.md`)
- [ ] SIMULATION_MODE validated in scripts (true)
- [ ] No hardcoded secrets in this PR

## Approvals
Request approvals from:
- Security Admin @security_team
- Ops Lead @ops_team
- Finance Owner @finance_team
- Governance Owner @governance_team

## How to reproduce locally (simulation)
```bash
# run quick validation (simulation)
SIMULATION_MODE=true make k-all-precheck
```

## Merge action

* On merge, tag `v1.0.0-release-candidate` and create a release draft with attached artifacts.