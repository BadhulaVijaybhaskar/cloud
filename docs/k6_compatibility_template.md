# K.6 Integration Plane Compatibility Template

## Overview
This template defines the K.6 Integration Plane compatibility requirements and testing procedures.

## Acceptance Criteria
- `reports/k6/k6_compatibility_report.json` exists and `.summary.overall_status` is `PASS_SIMULATION`
- `.summary.failed == 0` for endpoint checks
- Contract tests either pass or return explicit `simulated` wrappers — pytest exit code 0 preferred
- mTLS checks are `ok` or flagged `skipped` (with reason)
- Metadata sanitize smoke returns sanitized object or simulation confirmation
- CI job uploads `reports/k6/` artifacts

## Run Steps
1. `make k6-clean`
2. `make k6-precheck`
3. `pytest -q tests/k6/contract_tests.py`
4. `make k6-deploy` (simulation only)
5. `make k6-verify`

## Failure Handling
- If any health endpoint fails, mark report status `FAIL_ENDPOINTS`
- If contract pytest fails in live mode, abort and send notification
- If mTLS handshake fails for a TLS endpoint, mark as `FAIL_TLS`
- Never run terraform apply / helm install when `SIMULATION_MODE=true`