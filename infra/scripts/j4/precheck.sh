#!/bin/bash
set -e
echo "[J4] Starting precheck..."
kubectl get pods -A > reports/launch_day/precheck.log
vault status >> reports/launch_day/precheck.log
terraform -chdir=infra/terraform plan -no-color | tee reports/launch_day/terraform_plan.log
echo "[J4] Precheck complete."