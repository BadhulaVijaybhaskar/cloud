# PR: K.7 Partner & Developer Ecosystem (SIMULATION-ready)

## Summary
Adds partner onboarding portal, marketplace v2 sandbox + SDK stubs, contract tests, CI, Docker Compose sandbox, Vault policy placeholder, and scripts.

## Branch
prod-feature/k7.partner-ecosystem

## Files added
- services/partner-portal/...
- services/marketplace-v2/...
- services/partner-sandbox/...
- services/partner-onboard-worker/...
- infra/scripts/k7/*
- infra/vault/policies/k7_partner.hcl
- docker-compose.yml
- Makefile targets (k7-*)
- tests/k7/*

## How to run (simulation)
1. `make k7-precheck`
2. `make k7-deploy`
3. `make k7-seed`
4. `make k7-up`
5. Test endpoints (see below)
6. `make k7-verify`
7. `make k7-down`

## Approvals required
- Security Admin
- Ops Lead
- Governance Owner
- Legal (partner agreements)

## Notes
All actions default to `SIMULATION_MODE=true`. Do not set to false without approvals and K.8 signoffs.