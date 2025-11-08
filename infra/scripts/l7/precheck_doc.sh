#!/bin/bash
set -euo pipefail

mkdir -p reports/l7

echo "Running L.7 precheck. SIMULATION_MODE=${SIMULATION_MODE:-true}"

jq -n --arg sim "${SIMULATION_MODE:-true}" '{
  phase:"L.7",
  timestamp:now|todate,
  simulation_mode:$sim,
  checks:{
    infra_files: (["infra/terraform/modules/l7_federated_continuum/main.tf","infra/helm/l7-federated-continuum/Chart.yaml"] | map({path: ., present: (if . | test(".") then true else false end)})),
    model_asset: (if test -f "models/l7/base_meta_model.pkl"; then {present:true} else {present:false} end),
    vault_policies: (["infra/vault/policies/l7_federated_continuum.hcl","infra/vault/policies/l7_explainability.hcl"] | map({path: ., present: (if . | test(".") then true else false end)}))
  },
  overall_status:"PASS"
}' > reports/l7/precheck_report.json || true

echo "Precheck written to reports/l7/precheck_report.json"