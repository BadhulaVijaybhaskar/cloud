policy_matrix:
  data_ingest:
    policy_source: "Data Classification Policy"
    enforcement_point: "signal-gateway"
    enforcement_mode: "Reject/Mask"
    accept_criteria: "classified PII blocked unless token present"
    rules:
      - name: "pii_protection"
        condition: "classification == 'confidential' OR classification == 'restricted'"
        action: "require_consent_token"
      - name: "tenant_isolation"
        condition: "signal.metadata.tenant_id != null"
        action: "enforce_tenant_scope"
      - name: "data_masking"
        condition: "classification IN ['confidential', 'restricted']"
        action: "mask_sensitive_fields"

  model_updates:
    policy_source: "Model Governance Policy"
    enforcement_point: "fl-orchestrator"
    enforcement_mode: "Block pre-commit"
    accept_criteria: "tests pass, fairness metrics within bounds"
    rules:
      - name: "fairness_validation"
        condition: "fairness_score >= 0.8"
        action: "allow_aggregation"
      - name: "privacy_budget"
        condition: "epsilon_used <= epsilon_limit"
        action: "allow_aggregation"
      - name: "signature_validation"
        condition: "valid_signature == true"
        action: "allow_processing"

  access_control:
    policy_source: "IAM Policy"
    enforcement_point: "review-queue"
    enforcement_mode: "RBAC"
    accept_criteria: "step-up for sensitive approvals"
    rules:
      - name: "role_based_access"
        condition: "user.roles CONTAINS required_role"
        action: "grant_access"
      - name: "sensitive_review_mfa"
        condition: "review.sensitivity == 'high'"
        action: "require_mfa"
      - name: "admin_override"
        condition: "user.role == 'admin' AND justification != null"
        action: "allow_override"

  privacy_protection:
    policy_source: "Privacy Policy"
    enforcement_point: "privacy-proxy"
    enforcement_mode: "Transform"
    accept_criteria: "epsilon ≤ budget"
    rules:
      - name: "differential_privacy"
        condition: "aggregation_type == 'federated'"
        action: "apply_dp_noise"
      - name: "budget_tracking"
        condition: "cumulative_epsilon <= total_budget"
        action: "allow_operation"
      - name: "consent_validation"
        condition: "pii_present == true"
        action: "require_consent"

  explainability:
    policy_source: "Explainability Standard"
    enforcement_point: "explainability"
    enforcement_mode: "Advisory"
    accept_criteria: "explanation available for top-10 decisions"
    rules:
      - name: "high_impact_explanation"
        condition: "decision.impact >= 'high'"
        action: "generate_explanation"
      - name: "model_interpretability"
        condition: "model.type == 'ml_based'"
        action: "provide_feature_attribution"
      - name: "audit_trail_explanation"
        condition: "audit_required == true"
        action: "detailed_rationale"

  audit_compliance:
    policy_source: "Audit Policy"
    enforcement_point: "audit-log"
    enforcement_mode: "Append-only"
    accept_criteria: "immutability proof available"
    rules:
      - name: "immutable_logging"
        condition: "event.type IN ['decision', 'model_update', 'conflict_resolution']"
        action: "append_to_audit_log"
      - name: "integrity_verification"
        condition: "audit_entry != null"
        action: "generate_hash_chain"
      - name: "retention_policy"
        condition: "entry.age > retention_period"
        action: "archive_to_cold_storage"

enforcement_levels:
  - level: "block"
    description: "Prevent operation from proceeding"
    severity: "critical"
  - level: "transform"
    description: "Modify data/operation to comply"
    severity: "warning"
  - level: "audit"
    description: "Log violation but allow operation"
    severity: "info"
  - level: "advisory"
    description: "Recommend action but don't enforce"
    severity: "info"

compliance_requirements:
  gdpr:
    - "data_consent_tracking"
    - "right_to_erasure"
    - "data_portability"
  hipaa:
    - "phi_encryption"
    - "access_logging"
    - "minimum_necessary"
  sox:
    - "audit_trail_integrity"
    - "segregation_of_duties"
    - "change_management"