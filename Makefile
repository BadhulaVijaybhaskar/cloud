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

k9-clean:
	rm -rf reports/k9 || true