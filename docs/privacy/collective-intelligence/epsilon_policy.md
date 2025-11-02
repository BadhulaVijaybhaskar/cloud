# Privacy Budget (Epsilon) Policy - Phase I.5 CIN

## Overview

This document defines the privacy budget management policy for the Collective Intelligence Network (CIN) federated learning operations, implementing differential privacy guarantees.

## Privacy Budget Allocation

### Global Budget
- **Total Epsilon Budget**: 10.0 per tenant per month
- **Emergency Reserve**: 2.0 (20% of total budget)
- **Available for FL Rounds**: 8.0 per month

### Per-Round Allocation
- **Standard FL Round**: 0.5 epsilon maximum
- **High-Priority Round**: 1.0 epsilon maximum  
- **Emergency Round**: 2.0 epsilon maximum (requires approval)

### Budget Tracking
- Budget consumption tracked per tenant, per model, per time period
- Real-time budget monitoring with alerts at 75% and 90% consumption
- Automatic budget reset on monthly cycle
- Carry-over of unused budget up to 25% of monthly allocation

## Differential Privacy Parameters

### Noise Mechanisms
- **Gaussian Mechanism**: For continuous-valued queries
- **Laplace Mechanism**: For counting queries and histograms
- **Exponential Mechanism**: For categorical selections

### Privacy Accounting
- **Composition Method**: Advanced composition with tight bounds
- **Sensitivity Analysis**: Automated L1/L2 sensitivity calculation
- **Privacy Loss Tracking**: Real-time epsilon consumption monitoring

## FL Round Privacy Requirements

### Model Delta Privacy
```yaml
privacy_requirements:
  gradient_clipping:
    enabled: true
    max_norm: 1.0
  noise_addition:
    mechanism: "gaussian"
    sigma: 1.1  # Based on epsilon and delta parameters
  aggregation:
    method: "secure_sum"
    min_participants: 3
```

### Epsilon Allocation Strategy
1. **Gradient Computation**: 40% of round epsilon
2. **Model Update**: 40% of round epsilon  
3. **Validation Metrics**: 20% of round epsilon

## Policy Enforcement

### Pre-Round Validation
- Verify sufficient epsilon budget available
- Validate privacy parameters meet policy requirements
- Check participant count meets minimum threshold
- Confirm model sensitivity bounds

### Runtime Monitoring
- Track actual epsilon consumption during aggregation
- Monitor for privacy budget violations
- Alert on unexpected privacy loss patterns
- Automatic round termination if budget exceeded

### Post-Round Accounting
- Record actual epsilon consumed
- Update tenant budget balances
- Generate privacy audit reports
- Archive privacy parameters for compliance

## Compliance Requirements

### Data Residency
- Privacy computations must occur in tenant's designated regions
- Cross-border data transfer requires explicit consent
- Local privacy laws take precedence over global policy

### Audit Trail
- All privacy budget allocations logged immutably
- Privacy parameter decisions recorded with justification
- Regular privacy audits by independent third parties
- Compliance reports generated monthly

## Emergency Procedures

### Budget Exhaustion
1. Suspend new FL rounds for affected tenant
2. Notify tenant administrators immediately
3. Offer emergency budget allocation with approval
4. Investigate cause of unexpected consumption

### Privacy Breach Detection
1. Immediate suspension of all FL operations
2. Forensic analysis of privacy loss
3. Notification to affected parties within 24 hours
4. Remediation plan development and execution

## Implementation Guidelines

### Service Integration
- **FL Orchestrator**: Primary budget enforcement point
- **Privacy Proxy**: Noise addition and aggregation
- **Audit Log**: Privacy operation recording
- **Policy Engine**: Budget validation and alerts

### Monitoring Dashboards
- Real-time epsilon consumption by tenant
- Privacy budget utilization trends
- FL round privacy metrics
- Policy violation alerts and trends

## Review and Updates

- Policy reviewed quarterly by Privacy Board
- Updates require approval from Legal and Engineering teams
- Changes communicated to all tenants 30 days in advance
- Emergency updates may be implemented with 24-hour notice

---

**Policy Version**: 1.0  
**Effective Date**: 2025-01-11  
**Next Review**: 2025-04-11  
**Approved By**: CIN Privacy Board