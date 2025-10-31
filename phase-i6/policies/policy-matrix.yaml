# Policy matrix for ATOM Cloud — P1..P7 enforcement rules
# path: phase-i6/policies/policy-matrix.yaml
version: "1.0"
generated_by: "assistant"
generated_at: "2024-12-19T10:30:00Z"

policies:
  P1_Data_Privacy:
    id: P1
    title: "Data Privacy & PII Handling"
    description: |
      Protect user personal data. Block or redact PII at ingest unless explicit tenant consent and signed manifest present.
    enforcement_points:
      - signal-gateway
      - data-api
      - model-store
      - audit-log
    enforcement_mode: "reject_or_mask"
    rules:
      - name: "pii_detection_block"
        when: "ingest_event.contains_pii == true"
        action: "reject"            # unless consent token scope present
        exceptions:
          - require_scope: "pii:replicate"
          - require_signed_manifest: true
      - name: "pii_mask_logs"
        when: "event.logged == true"
        action: "mask"
    retention:
      logs_days: 30
      audit_days: 3650
    metadata:
      sensitivity_class: "high"

  P2_Secrets_and_Signing:
    id: P2
    title: "Secrets, Signing & Supply Chain"
    description: |
      All artifacts, manifests and deployable images must be signed. Keys stored in Vault; cosign enforced in production.
    enforcement_points:
      - model-store
      - deploy-orchestrator
      - registry-mirror-manager
      - policy-hub
    enforcement_mode: "block_if_unsigned"
    rules:
      - name: "artifact_cosign_check"
        when: "artifact.deploy_request"
        action: "require_cosign_signature"
      - name: "vault_presence"
        when: "env == production"
        action: "require_vault_addr"
    approver_required: true
    metadata:
      key_rotation_days: 90

  P3_Execution_Safety:
    id: P3
    title: "Execution Safety & Approval"
    description: |
      High-impact actions require approver and dry-run; automated actions default to dry_run unless risk_score < threshold.
    enforcement_points:
      - failover-orchestrator
      - arbiter
      - action-orchestrator
    enforcement_mode: "dry_run_then_approve"
    rules:
      - name: "high_impact_requires_approver"
        when: "action.impact == high"
        action: "require_approver"
      - name: "dry_run_default"
        when: "action.impact in [medium, high]"
        action: "force_dry_run"
    metadata:
      default_timeout_ms: 30000

  P4_Observability:
    id: P4
    title: "Observability & Metrics"
    description: |
      All services must export /health and /metrics; trace ids must flow end-to-end.
    enforcement_points:
      - all_services
    enforcement_mode: "monitoring"
    rules:
      - name: "health_endpoint"
        when: "service.deployed"
        action: "require /health"
      - name: "prometheus_metrics"
        when: "service.deployed"
        action: "require /metrics"
      - name: "trace_propagation"
        when: "request_flow"
        action: "require_trace_id"
    metadata:
      metrics_retention_days: 90

  P5_Multi_Tenancy:
    id: P5
    title: "Multi-Tenancy & Isolation"
    description: |
      Tenant data, compute, and policies must be isolated. RLS required on DB layers; network namespaces per tenant.
    enforcement_points:
      - data-api
      - neural-fabric-scheduler
      - inference-gateway
    enforcement_mode: "isolation"
    rules:
      - name: "db_rls"
        when: "db.table.multitenant == true"
        action: "require_rls"
      - name: "tenant_namespace"
        when: "deploy_request"
        action: "require_namespace"
    metadata:
      tenant_quota_defaults:
        cpu: "2"
        memory: "4Gi"

  P6_Performance_Budget:
    id: P6
    title: "Performance & SLOs"
    description: |
      Define SLOs and budget for latency/cost. Reject policy changes that may break P6.
    enforcement_points:
      - global-router
      - neural-autoscaler
      - fl-orchestrator
    enforcement_mode: "monitor_and_block_if_violate"
    rules:
      - name: "p95_latency_target"
        when: "service == global-router"
        action: "must_meet_p95_ms"
        threshold_ms: 500
      - name: "neural_schedule_budget"
        when: "gpu_schedule"
        action: "respect_node_budget"
    metadata:
      cost_alert_threshold_pct: 20

  P7_Resilience_and_Recovery:
    id: P7
    title: "Resilience, Snapshots & Recovery"
    description: |
      Snapshot state before critical changes. Maintain immutable audit and rollback plan.
    enforcement_points:
      - deploy-orchestrator
      - failover-orchestrator
      - audit-log
    enforcement_mode: "snapshot_and_audit"
    rules:
      - name: "pre_change_snapshot"
        when: "action.type in [promote, deploy, schema_migration]"
        action: "take_snapshot"
      - name: "immutable_audit"
        when: "audit_entry"
        action: "append_only"
    metadata:
      snapshots_retention_days: 90