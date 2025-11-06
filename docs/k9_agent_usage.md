# K.9 Agent Usage (1-page)

- Default: SIMULATION_MODE=true
- Run precheck: `make k9-precheck`
- Simulated deploy: `make k9-deploy`
- Run tests: `make k9-test`
- Live deploy (operator only): set APPROVE_K9_DEPLOY=yes and SIMULATION_MODE=false and run infra/scripts/k9/deploy.sh
- Reports: reports/k9/precheck_report.json, deploy_summary.json, simulation_*.json