K.8 Pre-Production Checklist (Simulation-first)

- [x] Run `make k8-precheck` (SIMULATION_MODE=true)
- [x] Run `make k8-deploy`
- [x] Run `make k8-reconcile`
- [x] Run `make k8-verify`
- [x] Collect reports from `reports/k8/` and attach to PR
- [ ] Obtain approvals: Security Admin, Ops Lead, Governance Owner, Finance Owner
- [ ] For live deployment: set SIMULATION_MODE=false and APPROVE_K8_DEPLOY=yes then run infra/scripts/k8/deploy_k8.sh