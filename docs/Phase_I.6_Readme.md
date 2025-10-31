# Phase I.6 - Adaptive Optimization Layer (AOL)

## Overview
The Adaptive Optimization Layer (AOL) is an intelligent system that continuously monitors telemetry, proposes parameter optimizations, validates changes through simulation and canary deployments, and applies optimizations with full auditability and rollback capabilities.

## Architecture

### Core Components
1. **AOL Controller** (`services/aol-controller/`) - Main optimization engine
2. **AOL UI Proxy** (`services/aol-ui-proxy/`) - LaunchPad integration API
3. **Policy Engine Integration** - P1-P7 compliance enforcement
4. **Database Schema** - Persistent storage for proposals and audit

### Key Features
- **ML-Driven Optimization**: EWMA-based metric analysis with threshold detection
- **Risk Assessment**: Automatic risk classification and approval workflows
- **Canary Deployments**: Safe rollout with automatic rollback
- **Explainable AI**: Human-readable rationale for all optimization decisions
- **Full Auditability**: Immutable audit trail with cryptographic signatures

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional - uses simulation mode if not available)
- Docker (for containerized deployment)

### Local Development
```bash
# Set simulation mode
export SIMULATION_MODE=true

# Start AOL Controller
cd services/aol-controller
pip install -r requirements.txt
python main.py

# Start UI Proxy (separate terminal)
cd services/aol-ui-proxy
pip install -r requirements.txt
python main.py
```

## API Usage

### Submit Optimization Proposal
```bash
curl -X POST http://localhost:8601/v1/propose \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "tenant:demo",
    "changes": [{"path": "scheduler.cpu_limit", "value": 1.2}],
    "risk_level": "low",
    "reason": "CPU optimization"
  }'
```

## Policy Compliance (P1-P7)
- **P1**: PII detection and data anonymization
- **P2**: Cosign signing and Vault integration
- **P3**: Risk-based approval workflows
- **P4**: Prometheus metrics and health checks
- **P5**: Tenant isolation and RLS
- **P6**: SLO monitoring and enforcement
- **P7**: State snapshots and audit trails