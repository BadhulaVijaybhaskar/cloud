# Checklist: Preconditions & Approvals to Run Live Production Cutover (Phase J.5)

**Environment:** production (`atom-prod`)  
**Target Release:** `v1.2.0-stable-prod`  
**Date / Time:** ___________ (set before deploy)  
**Operator / Approver:** ___________

> IMPORTANT: The live deployment script `infra/scripts/j5/run_launch_day.sh` will refuse to run unless `APPROVE_DEPLOY=yes` is set. This checklist must be completed and recorded in `reports/j5/run_approvals.json` before flipping `SIMULATION_MODE=false`.

---

## 1. Governance & Policy Gates (Security Admin)
- [ ] I9 Governance report present: `reports/I9_governance_test_report.json`  
- [ ] P1–P20 compliance: checks passed and evidence attached (list file names)  
- [ ] Policy exception log: empty or documented with approval (file: `reports/j5/policy_exceptions.json`)

**Security Admin (name / sig):** ____________________  Date: ___________

---

## 2. Secrets & Vault
- [ ] Vault reachable and unsealed (`vault status` output in `reports/j5/precheck_prod.log`)  
- [ ] Vault policy files present: `infra/vault/policies/*.hcl`  
- [ ] Production secrets mapping reviewed (location & rotation policy)  
- [ ] `VAULT_TOKEN` provisioning plan documented; token lifecycle reviewed

**Security Admin (name / sig):** ____________________  Date: ___________

---

## 3. Infrastructure & Configuration
- [ ] Terraform plan reviewed and saved: `reports/j5/terraform_plan_prod.log`  
- [ ] Helm charts linted and templated: outputs in `reports/j5/*.helm.tpl.yaml`  
- [ ] `serviceMesh.enabled` flag verified for production values  
- [ ] Node pool & cluster capacity validated for canary + scale targets

**Ops Engineer (name / sig):** ____________________  Date: ___________

---

## 4. Monitoring & Alerting
- [ ] Prometheus targets healthy: check `reports/j5/monitoring_snapshot.json`  
- [ ] Grafana dashboards available and shared with on-call team  
- [ ] Alertmanager routes tested; test alert observed in channel `#ops-alerts`  
- [ ] PagerDuty escalation tested (triggered and acknowledged)

**SRE Lead (name / sig):** ____________________  Date: ___________

---

## 5. CI/CD & Artifact Validation
- [ ] Docker images built & checksum verified (list image tags)  
- [ ] Images pushed to prod registry: `registry.atomcloud.io` (yes/no)  
- [ ] Release tag created: `v1.2.0-stable-prod`  
- [ ] Signed artifacts (Cosign) present and verified

**CI/CD Owner (name / sig):** ____________________  Date: ___________

---

## 6. Billing & Metering
- [ ] Billing endpoints verified (sandbox) — `reports/j5/billing_sanity.json`  
- [ ] Metering reconciliation script present and smoke-tested  
- [ ] Alert on unexpected billing spikes configured

**Billing Owner (name / sig):** ____________________  Date: ___________

---

## 7. Partner Federation
- [ ] Partner registry contract & metadata present: `infra/contracts/partners/federation_registry.json`  
- [ ] Test partner credentials set and verified (PartnerA / PartnerB)  
- [ ] Federation call flows smoke-tested and successful

**Partner Onboarding Lead (name / sig):** ____________________  Date: ___________

---

## 8. Runbooks & Rollbacks
- [ ] Launch day runbook present: `docs/runbooks/launch_day_runbook.md`  
- [ ] Rollback script present and validated: `infra/scripts/j5/rollback_prod.sh`  
- [ ] Rollback drill rehearsed (dry-run) within the last 7 days

**Program Lead (name / sig):** ____________________  Date: ___________

---

## 9. Communications & Stakeholders
- [ ] Launch announcement drafted (Slack / mail) and approved  
- [ ] Business stakeholders informed of maintenance window  
- [ ] External partner communications prepared (if applicable)

**Communications Owner (name / sig):** ____________________  Date: ___________

---

## 10. Final Operator Approval (required to run live)
- I, the operator, confirm that all the above checks are complete and I accept responsibility to execute the production cutover.

**Operator Name:** ____________________  
**Operator Signature (or Git commit hash):** ____________________  
**APPROVE_DEPLOY flag to set before running:** `export APPROVE_DEPLOY=yes`

Date / Time of live run: _______________  Timezone: _______________

---

## Post-Approval Procedure
1. Export env:
```bash
export SIMULATION_MODE=false
export APPROVE_DEPLOY=yes
export VAULT_TOKEN="<vault-token-provided-securely>"
```

2. Run:
```bash
./infra/scripts/j5/run_launch_day.sh
```

3. Monitor dashboards and keep the on-call roster active for at least 72 hours.

**Record of Approval saved to:** `reports/j5/run_approvals.json` (operator must create after sign-off)

---

## Emergency Contact List (for live run)

* Ops Lead: ops@atomcloud.io / +91-XXXXX
* SRE Lead: sre@atomcloud.io / +91-XXXXX
* Security Admin: secadmin@atomcloud.io / +91-XXXXX
* Program Lead: lead@atomcloud.io / +91-XXXXX

---

**End of Checklist**
Save this file in `docs/checklist_to_run_live.md` and attach completed checklist and signatures to `reports/j5/run_approvals.json` before running live.