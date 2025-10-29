# Self-Host Compliance Policy

## Overview
Policy enforcement for self-hosted ATOM Cloud deployments ensuring P1-P7 compliance across all cluster nodes.

## Policy Matrix

| Policy | Requirement | Enforcement |
|:-------|:------------|:------------|
| P1 | Tenant data isolated per namespace | NetworkPolicy + RBAC |
| P2 | Charts and secrets cosign-signed | Admission controller |
| P3 | Playbooks dry-run by default | Ansible --check flag |
| P4 | /metrics export for each daemon | Prometheus scraping |
| P5 | One namespace per tenant | Resource quotas |
| P6 | Provision < 2 min simulation budget | Performance monitoring |
| P7 | Auto rollback on failure | Helm rollback hooks |

## Monitoring
- Policy violations logged to audit trail
- Compliance dashboard at /metrics endpoint
- Automated remediation for P1, P5, P7

## Simulation Mode
All policies report COMPLIANT in simulation mode with mock validation.