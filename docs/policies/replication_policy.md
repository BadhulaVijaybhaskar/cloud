# Replication Policy (enforces P1–P7 for replication)

## Overview
This file codifies safe replication practices for ATOM Cross-Cloud replication.

## Rules
- P1 Data Privacy
  - Raw PII must never be replicated without explicit tenant consent.
  - If tenant consents, manifest must include `pii:replicate` flag and approver.
- P2 Secrets & Signing
  - All replication manifests must be cosign-signed before activation.
  - Any change to replication topology requires an audit entry.
- P3 Execution Safety
  - Failover or promote actions require `approved_by` user and recorded justification.
  - Dry-run is mandatory prior to production switchover.
- P4 Observability
  - Each replication worker exposes `/health` and `/metrics`.
  - Replication metrics must include labels: `phase="G.2"`, `service=<name>`, `tenant=<id>`.
- P5 Multi-Tenancy
  - Replication jobs must include `tenant_id`.
  - Controllers must validate JWT tenant context.
- P6 Performance Budget
  - Large datasets must be chunked and scheduled outside peak window; respect `REPLICATION_WINDOW_MS`.
- P7 Resilience & Recovery
  - Snapshot uploads must include `sha256` and be validated on restore.
  - Test-run (resilience testbench) required on major topology changes.

## Enforcement
- Policy Gatekeeper and replication-controller validate these rules.
- Violations block activation and require human approval.