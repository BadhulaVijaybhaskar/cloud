# Router Policy Framework

## Overview
Global router policy enforcement ensuring P1-P7 compliance across all routing decisions.

## Policy Structure
```json
{
  "version": "1.0.0",
  "tenant_policies": {
    "tenant-1": {
      "geo_affinity": ["us-east-1", "us-west-2"],
      "rate_limit_rps": 1000,
      "priority": "high"
    }
  },
  "global_rules": {
    "p1_tenant_isolation": true,
    "p2_signature_required": true,
    "p6_latency_slo_ms": 100
  }
}
```

## Policy Enforcement
- P1: Tenant routing isolation via namespace policies
- P2: All policies must be cosign-signed
- P4: Routing metrics exported to Prometheus
- P5: One policy namespace per tenant
- P6: p95 latency SLO enforced per decision
- P7: Auto rollback on policy validation failure

## Simulation Mode
All policies report COMPLIANT in simulation with mock signature verification.