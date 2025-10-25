# WPK Static Validation Policy Rules

## Overview

This document defines the static validation rules and security policies applied to WPK (Workflow Package) files during dry-run validation.

## Security Categories

### 1. Critical Security Issues (Risk Score: 90-100)

#### Privileged Container Access
- **Rule**: `privileged: true` in container specifications
- **Risk**: Full host access, container escape potential
- **Action**: Block execution, require manual approval

#### Host Path Mounts
- **Rule**: `hostPath` volume mounts to sensitive directories
- **Sensitive Paths**: `/`, `/etc`, `/var/run/docker.sock`, `/proc`, `/sys`
- **Action**: Block execution, suggest alternatives

#### Dangerous Capabilities
- **Rule**: Linux capabilities that grant excessive privileges
- **Dangerous Caps**: `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`
- **Action**: Block execution, require justification

### 2. High Security Issues (Risk Score: 70-89)

#### Cluster-Level Permissions
- **Rule**: ClusterRole or ClusterRoleBinding modifications
- **Risk**: Cluster-wide privilege escalation
- **Action**: Require approval, audit logging

#### External Network Calls
- **Rule**: HTTP/HTTPS requests to external domains
- **Patterns**: `curl`, `wget` commands to external URLs
- **Action**: Validate necessity, whitelist domains

### 3. Medium Security Issues (Risk Score: 40-69)

#### Resource Limits
- **Rule**: Missing or excessive resource requests/limits
- **Thresholds**: CPU > 4 cores, Memory > 8Gi, Storage > 100Gi
- **Action**: Optimize resource usage

## Risk Scoring Algorithm

```python
def calculate_risk_score(issues):
    base_score = 0
    for issue in issues:
        if issue.severity == "critical": base_score += 25
        elif issue.severity == "high": base_score += 15
        elif issue.severity == "medium": base_score += 10
        elif issue.severity == "low": base_score += 5
    return min(100, base_score)
```

## Policy Decision Matrix

| Risk Score | Safety Mode | Decision | Action Required |
|------------|-------------|----------|-----------------|
| 0-25 | auto | approve | None |
| 26-50 | auto | review | Security team review |
| 51-75 | auto | block | Security approval required |
| 76-100 | any | block | CISO approval required |