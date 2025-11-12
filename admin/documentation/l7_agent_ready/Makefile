.PHONY: l7-precheck l7-deploy l7-verify l7-rollback
l7-precheck:
	SIMULATION_MODE=true bash infra/scripts/l7/precheck.sh

l7-deploy:
	SIMULATION_MODE=true bash infra/scripts/l7/deploy.sh

l7-verify:
	SIMULATION_MODE=true bash infra/scripts/l7/verify.sh

l7-rollback:
	bash infra/scripts/l7/rollback.sh
