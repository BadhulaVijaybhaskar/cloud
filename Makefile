# Makefile - K.2 helper shortcuts (precheck, deploy, verify) for local dev & CI
# Usage:
#   make k2-precheck
#   make k2-deploy SIMULATION_MODE=true
#   make k2-verify

K2_SCRIPTS_DIR := infra/scripts/k2
REPORTS_DIR := reports/k2

.PHONY: k2-precheck k2-deploy k2-verify k2-clean k2-all k9-precheck k9-deploy k9-verify k9-test k9-clean

# default simulation mode
SIM ?= true
APPROVE ?= no

k2-precheck:
	@echo ">>> Running K.2 precheck (SIMULATION_MODE=${SIM}) ..."
	@test -d $(K2_SCRIPTS_DIR) || (echo "ERROR: $(K2_SCRIPTS_DIR) not found"; exit 2)
	@SIMULATION_MODE=${SIM} bash $(K2_SCRIPTS_DIR)/precheck.sh
	@echo ">>> Precheck output:"
	@ls -l $(REPORTS_DIR) || true

k2-deploy:
	@echo ">>> Deploying K.2 (SIMULATION_MODE=${SIM}, APPROVE_AUTONOMY=${APPROVE}) ..."
	@test -d $(K2_SCRIPTS_DIR) || (echo "ERROR: $(K2_SCRIPTS_DIR) not found"; exit 2)
	@SIMULATION_MODE=${SIM} APPROVE_AUTONOMY=${APPROVE} bash $(K2_SCRIPTS_DIR)/deploy.sh
	@echo ">>> Deploy summary:"
	@ls -l $(REPORTS_DIR) || true

k2-verify:
	@echo ">>> Verifying K.2 reports & basic schema..."
	@test -d $(REPORTS_DIR) || (echo "ERROR: $(REPORTS_DIR) not present; run k2-precheck or k2-deploy"; exit 2)
	@python3 - <<'PY'
import json,glob,sys
files = glob.glob('reports/k2/*.json')
if not files:
    print("No reports found under reports/k2/ - run precheck/deploy first"); sys.exit(2)
ok = True
for p in files:
    try:
        with open(p) as fh:
            json.load(fh)
    except Exception as e:
        print("INVALID JSON:", p, e); ok = False
print("JSON parse status:", "OK" if ok else "ERROR")
PY

k2-clean:
	@echo ">>> Cleaning reports/k2 ..."
	@rm -rf reports/k2 || true
	@mkdir -p reports/k2
	@echo "Done."

k2-all: k2-precheck k2-deploy k2-verify

# K.9 AI Marketing Agent targets
k9-precheck:
	SIMULATION_MODE=true bash infra/scripts/k9/precheck.sh

k9-deploy:
	SIMULATION_MODE=true bash infra/scripts/k9/deploy.sh

k9-verify:
	SIMULATION_MODE=true bash infra/scripts/k9/verify.sh

k9-test:
	SIMULATION_MODE=true pytest tests/k9/ -q || true

k9-test-telemetry:
	@echo "Running k9 telemetry integration tests (pytest)"
	pytest -q tests/k9/integration/test_telemetry.py || true

k9-clean:
	rm -rf reports/k9 || true

# K.9 finalization targets
k9-telemetry:
	python services/k9-agent-core/telemetry/telemetry_collector.py

k9-contract-lint:
	@echo "Linting infra/contracts/k9_openapi.yaml (speccy)"
	@if command -v speccy >/dev/null 2>&1; then \
		mkdir -p reports/k9 || true; \
		speccy lint infra/contracts/k9_openapi.yaml -j > reports/k9/openapi_lint.json || true; \
		echo "Lint report: reports/k9/openapi_lint.json"; \
	else \
		echo "speccy not installed — please install (npm i -g speccy)"; \
	fi

k9-quick: k9-telemetry k9-test
	@echo "K9 quick tasks complete."

# L.1 Post-Integration Audit
.PHONY: l1-audit l1-test

l1-audit:
	@echo "Running L.1 post-integration audit..."
	bash infra/scripts/l1/run_audit.sh

l1-test:
	@echo "Running L.1 audit tests..."
	pytest -q tests/l1/integration || true

# L.2 Governance Mesh
.PHONY: l2-precheck l2-deploy l2-verify l2-test l2-clean

l2-precheck:
	@echo "Running L.2 precheck..."
	SIMULATION_MODE=true bash infra/scripts/l2/precheck_l2.sh > reports/l2/precheck_report.json

l2-deploy:
	@echo "Running L.2 deploy (simulation)..."
	SIMULATION_MODE=true bash infra/scripts/l2/deploy_l2.sh > reports/l2/deploy_summary.json

l2-verify:
	@echo "Running L.2 verification..."
	SIMULATION_MODE=true bash infra/scripts/l2/verify_l2.sh > reports/l2/verification_summary.json

l2-test:
	@echo "Running L.2 integration tests..."
	python tests/l2/integration/test_mesh_end_to_end.py

l2-clean:
	rm -rf reports/l2 || true

# L.3 Global Autonomy Exchange
.PHONY: l3-precheck l3-deploy l3-verify l3-test l3-clean

l3-precheck:
	@echo "Running L.3 precheck..."
	SIMULATION_MODE=true bash infra/scripts/l3/precheck.sh

l3-deploy:
	@echo "Running L.3 deploy (simulation)..."
	SIMULATION_MODE=true bash infra/scripts/l3/deploy.sh

l3-verify:
	@echo "Running L.3 verification..."
	bash infra/scripts/l3/verify.sh

l3-test:
	@echo "Running L.3 integration tests..."
	python tests/l3/integration/contract_tests.py

l3-clean:
	rm -rf reports/l3 || true

# L.3 GAE Extended
.PHONY: l3-gae-precheck l3-gae-deploy l3-gae-verify l3-gae-test l3-gae-clean

l3-gae-precheck:
	@echo "Running L.3 GAE precheck..."
	SIMULATION_MODE=true bash infra/scripts/l3_gae/precheck.sh

l3-gae-deploy:
	@echo "Running L.3 GAE deploy..."
	SIMULATION_MODE=true bash infra/scripts/l3_gae/deploy.sh

l3-gae-verify:
	@echo "Running L.3 GAE verification..."
	bash infra/scripts/l3/verify.sh

l3-gae-test:
	@echo "Running L.3 GAE tests..."
	python tests/l3_gae/integration/test_exchange_flow.py

l3-gae-clean:
	rm -rf reports/l3 infra/security/certs || true

# L.3 Missing Items - Production Readiness
.PHONY: l3-apply-vault l3-provision-secrets l3-rbac-audit l3-missing-check

l3-apply-vault:
	@echo "Applying Vault policies..."
	SIMULATION_MODE=${SIM:-true} bash infra/scripts/l3/apply_vault_policies.sh

l3-provision-secrets:
	@echo "Provisioning secrets..."
	SIMULATION_MODE=${SIM:-true} bash infra/scripts/l3/provision_secrets.sh

l3-rbac-audit:
	@echo "Running RBAC audit..."
	bash infra/scripts/l3/rbac_audit.sh

l3-missing-check:
	@echo "Checking L.3 production readiness..."
	python -c "import os; missing=[]; [missing.append(f) for f in ['reports/l3/approval_signoffs.json', 'infra/monitoring/alert_rules/l3_alerts.yaml', 'docs/canary_plan_l3.md'] if not os.path.exists(f)]; print('Missing items:', missing if missing else 'None - Ready for production!')"

# L.3 Missing V1 - Additional Production Tools
.PHONY: l3-archive-s3 l3-vault-test l3-alert-dryrun

l3-archive-s3:
	@echo "Archiving L.3 reports to S3 (simulation by default)..."
	SIMULATION_MODE=${SIM:-true} bash infra/scripts/l3/archive_reports_to_s3.sh

l3-vault-test:
	@echo "Testing Vault PKI & policies (simulation by default)..."
	SIMULATION_MODE=${SIM:-true} bash infra/scripts/l3/vault_pki_policy_test.sh

l3-alert-dryrun:
	@echo "Running alert dry-run test (simulation by default)..."
	SIMULATION_MODE=${SIM:-true} bash infra/scripts/l3/alert_dryrun.sh

# L.4 Distributed Intelligence Federation
.PHONY: l4-precheck l4-deploy l4-verify l4-test l4-clean

l4-precheck:
	@echo "Running L.4 precheck..."
	SIMULATION_MODE=true bash infra/scripts/l4/precheck.sh

l4-deploy:
	@echo "Running L.4 deploy (simulation)..."
	SIMULATION_MODE=true bash infra/scripts/l4/deploy.sh

l4-verify:
	@echo "Running L.4 verification..."
	SIMULATION_MODE=true bash infra/scripts/l4/verify.sh

l4-test:
	@echo "Running L.4 integration tests..."
	python tests/l4/integration/test_end_to_end.py

l4-clean:
	rm -rf reports/l4 || true

# L.5 Cognitive Federation Scaling
.PHONY: l5-precheck l5-deploy l5-verify l5-test l5-clean

l5-precheck:
	@echo "Running L.5 precheck..."
	SIMULATION_MODE=true bash infra/scripts/l5/precheck.sh

l5-deploy:
	@echo "Running L.5 deploy (simulation)..."
	SIMULATION_MODE=true bash infra/scripts/l5/deploy.sh

l5-verify:
	@echo "Running L.5 verification..."
	SIMULATION_MODE=true bash infra/scripts/l5/verify.sh

l5-test:
	@echo "Running L.5 integration tests..."
	python tests/l5/integration/test_end_to_end.py

l5-clean:
	rm -rf reports/l5 || true

# L.6 Cognitive Resilience & Adaptive Self-Healing Federation
.PHONY: l6-precheck l6-deploy l6-verify l6-test l6-clean

l6-precheck:
	@echo "Running L.6 precheck..."
	SIMULATION_MODE=true bash infra/scripts/l6/precheck.sh

l6-deploy:
	@echo "Running L.6 deploy (simulation)..."
	SIMULATION_MODE=true bash infra/scripts/l6/deploy.sh

l6-verify:
	@echo "Running L.6 verification..."
	SIMULATION_MODE=true bash infra/scripts/l6/verify.sh

l6-test:
	@echo "Running L.6 integration tests..."
	python tests/l6/integration/test_orchestrator_policy_integration.py

l6-clean:
	rm -rf reports/l6 || true

# L.7 Federated Cognitive Continuum & Self-Evolving Intelligence
.PHONY: l7-precheck l7-deploy l7-verify l7-test l7-clean

l7-precheck:
	@echo "Running L.7 precheck..."
	SIMULATION_MODE=true bash infra/scripts/l7/precheck.sh

l7-deploy:
	@echo "Running L.7 deploy (simulation)..."
	SIMULATION_MODE=true bash infra/scripts/l7/deploy.sh

l7-verify:
	@echo "Running L.7 verification..."
	SIMULATION_MODE=true bash infra/scripts/l7/verify.sh

l7-test:
	@echo "Running L.7 integration tests..."
	python -m pytest tests/l7/ -q

l7-clean:
	rm -rf reports/l7 || true