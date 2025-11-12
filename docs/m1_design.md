# M.1 Global Autonomous Certification & Cross-Domain Intelligence Exchange

## Overview

M.1 implements a trust, attestation, and exchange layer enabling certified intelligence sharing across ATOM federations while enforcing P43–P46 governance policies.

## Architecture

### Services

1. **GCA Core (m1-gca-core)** - Port 9200
   - Global Certification Authority
   - Signs/verifies cross-federation attestations
   - Issues short-lived audit tokens

2. **Intelligence Exchange Bus (m1-ix-bus)** - Port 9210
   - Encrypted message bus for attestation + intelligence deltas
   - Publishes/subscribes attestation envelopes

3. **Cross-Domain Policy Bridge (m1-cdp-bridge)** - Port 9220
   - Translates/enforces policy deltas between domains
   - Produces compatibility scores

4. **Federation Auditor (m1-fed-auditor)** - Port 9230
   - Stores immutable audit events
   - Verifies proofs, exposes query API

5. **Meta-Metrics Service (m1-meta-metrics)** - Port 9240
   - Aggregates anonymized statistics about cross-domain exchanges

## Governance Policies

- **P43**: Multi-role approval for key operations
- **P44**: Cross-domain policy validation
- **P45**: Audit trail enforcement
- **P46**: Compliance reporting

## Deployment

All services default to `SIMULATION_MODE=true` for safe testing. Production deployment requires explicit approval and `APPROVE_M1_DEPLOY=yes`.

## Security

- Signing keys are simulated in development
- Vault policies enforce governance requirements
- All operations are audited and logged