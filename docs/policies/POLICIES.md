# Global Policies (enforced across Phase D)

P-1 Data Privacy
- No raw PII stored in model inputs.
- Streams must anonymize IPs and identifiers.
- Storage only stores aggregated features for training.

P-2 Secrets & Signing
- All secrets must be in Vault or injected at runtime via CSI.
- All WPKs and models must be signed with cosign.
- Edge agents must validate signatures before execution.

P-3 Execution Safety
- Default safety.mode = manual.
- Any WPK labelled `auto` must have `dry_run` pass and an approver recorded before execution.
- Orchestrator must record approver id, justification, and sha256 of before/after state.

P-4 Observability
- Each service must expose `/metrics` (Prometheus) and `/health`.
- Distributed tracing via OpenTelemetry where available.

P-5 Multi-Tenancy
- Every request must carry tenant id in JWT.
- Postgres RLS or equivalent must enforce tenant isolation.

P-6 Performance Budget
- Agent actions must meet latency SLOs (p95 <= 800ms in staging).
- Long-running jobs must be asynchronous with progress telemetry.

P-7 Real-time Safety
- Agents require circuit-breaker and rate limiting on remediation actions.
- Execution requests must include idempotency tokens.

P-8 Cost Control
- Streaming producers must respect `STREAM_COST_BUDGET`; fall back to sampling when exceeded.

Enforcement:
- CI / registry validator / policy-learner must check P-1..P-8.