import pytest
import sys
from pathlib import Path

# Add the service directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "workflow-registry"))

from validator import WorkflowValidator, PolicyEngine, SafetyMode, PolicyDecision, ValidationResult, create_validator

@pytest.fixture
def validator():
    """Create validator instance"""
    return WorkflowValidator()

@pytest.fixture
def policy_engine():
    """Create policy engine instance"""
    return PolicyEngine()

@pytest.fixture
def valid_wpk():
    """Valid WPK for testing"""
    return {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "author": "Test Author",
            "signature": "test-signature"
        },
        "spec": {
            "runtime": {
                "type": "k8s",
                "requirements": {
                    "cpu": "100m",
                    "memory": "128Mi"
                }
            },
            "safety": {
                "mode": "manual",
                "approval_required": True,
                "dry_run_required": True
            },
            "handlers": [
                {
                    "name": "test-handler",
                    "type": "k8s",
                    "config": {
                        "action": "logs",
                        "namespace": "development"
                    },
                    "timeout": "30s"
                }
            ],
            "rollback": {
                "enabled": True,
                "handlers": []
            },
            "monitoring": {
                "metrics_enabled": True
            }
        }
    }

@pytest.fixture
def auto_wpk():
    """Auto mode WPK for testing"""
    return {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "auto-workflow",
            "version": "1.0.0",
            "description": "Auto workflow",
            "author": "Test Author",
            "signature": "test-signature"
        },
        "spec": {
            "runtime": {"type": "k8s"},
            "safety": {
                "mode": "auto",
                "dry_run_required": True
            },
            "handlers": [
                {
                    "name": "auto-handler",
                    "type": "k8s",
                    "config": {
                        "action": "scale",
                        "namespace": "production",
                        "replicas": 5
                    }
                }
            ],
            "rollback": {"enabled": True},
            "monitoring": {"metrics_enabled": True}
        }
    }

def test_validator_creation():
    """Test validator factory function"""
    validator = create_validator()
    assert isinstance(validator, WorkflowValidator)
    assert isinstance(validator.policy_engine, PolicyEngine)

def test_validate_wpk_structure_valid(validator, valid_wpk):
    """Test valid WPK structure validation"""
    result = validator.validate_wpk_structure(valid_wpk)
    
    assert result.valid is True
    assert len(result.errors) == 0

def test_validate_wpk_structure_missing_fields(validator):
    """Test WPK validation with missing fields"""
    invalid_wpk = {
        "apiVersion": "v1",
        "kind": "WorkflowPackage"
        # Missing metadata and spec
    }
    
    result = validator.validate_wpk_structure(invalid_wpk)
    
    assert result.valid is False
    assert "Missing required field: metadata" in result.errors
    assert "Missing required field: spec" in result.errors

def test_validate_wpk_structure_invalid_version(validator, valid_wpk):
    """Test WPK validation with invalid version format"""
    valid_wpk["metadata"]["version"] = "invalid-version"
    
    result = validator.validate_wpk_structure(valid_wpk)
    
    assert result.valid is False
    assert any("Invalid version format" in error for error in result.errors)

def test_validate_wpk_structure_no_handlers(validator, valid_wpk):
    """Test WPK validation with no handlers"""
    valid_wpk["spec"]["handlers"] = []
    
    result = validator.validate_wpk_structure(valid_wpk)
    
    assert result.valid is False
    assert "No handlers defined" in result.errors

def test_validate_wpk_structure_invalid_handler(validator, valid_wpk):
    """Test WPK validation with invalid handler"""
    valid_wpk["spec"]["handlers"] = [
        {
            "name": "invalid-handler"
            # Missing type and config
        }
    ]
    
    result = validator.validate_wpk_structure(valid_wpk)
    
    assert result.valid is False
    assert "Handler 0: missing type" in result.errors
    assert "Handler 0: missing config" in result.errors

def test_validate_policies_manual_mode(validator, valid_wpk):
    """Test policy validation for manual mode workflow"""
    result = validator.validate_policies(valid_wpk)
    
    assert result.valid is True
    assert result.policy_decision == PolicyDecision.ALLOW
    assert not result.approval_required

def test_validate_policies_auto_mode_denied(validator, auto_wpk):
    """Test policy validation for auto mode in production (should be denied)"""
    result = validator.validate_policies(auto_wpk)
    
    assert result.valid is False
    assert result.policy_decision == PolicyDecision.DENY
    assert "Auto mode denied for namespace: production" in result.errors

def test_validate_policies_auto_mode_requires_approval(validator, auto_wpk):
    """Test policy validation for auto mode requiring approval"""
    # Change to development namespace
    auto_wpk["spec"]["handlers"][0]["config"]["namespace"] = "development"
    
    result = validator.validate_policies(auto_wpk)
    
    assert result.valid is True
    assert result.policy_decision == PolicyDecision.REQUIRE_APPROVAL
    assert result.approval_required

def test_validate_policies_resource_limits(validator, valid_wpk):
    """Test policy validation for resource limits"""
    # Set excessive CPU
    valid_wpk["spec"]["runtime"]["requirements"]["cpu"] = "8000m"
    
    result = validator.validate_policies(valid_wpk)
    
    assert result.valid is False
    assert result.policy_decision == PolicyDecision.DENY
    assert any("CPU request" in error for error in result.errors)

def test_validate_policies_unsigned_workflow(validator, valid_wpk):
    """Test policy validation for unsigned workflow"""
    del valid_wpk["metadata"]["signature"]
    
    result = validator.validate_policies(valid_wpk)
    
    assert result.valid is False
    assert result.policy_decision == PolicyDecision.DENY
    assert "Workflow must be signed" in result.errors

def test_validate_policies_no_rollback(validator, valid_wpk):
    """Test policy validation without rollback"""
    valid_wpk["spec"]["rollback"]["enabled"] = False
    
    result = validator.validate_policies(valid_wpk)
    
    assert result.valid is True
    assert result.policy_decision == PolicyDecision.REQUIRE_APPROVAL
    assert result.approval_required
    assert "Rollback must be enabled" in result.warnings

def test_dry_run_validation_k8s_handler(validator, valid_wpk):
    """Test dry-run validation for k8s handler"""
    # Add scaling handler
    valid_wpk["spec"]["handlers"].append({
        "name": "scale-handler",
        "type": "k8s",
        "config": {
            "action": "scale",
            "replicas": 15
        }
    })
    
    result = validator.dry_run_validation(valid_wpk)
    
    assert result.valid is True
    assert any("Scaling to 15 replicas" in warning for warning in result.warnings)

def test_dry_run_validation_shell_handler(validator, valid_wpk):
    """Test dry-run validation for shell handler"""
    valid_wpk["spec"]["handlers"] = [{
        "name": "shell-handler",
        "type": "shell",
        "config": {
            "command": "rm -rf /tmp/test"
        }
    }]
    
    result = validator.dry_run_validation(valid_wpk)
    
    assert result.valid is True
    assert any("Potentially dangerous command" in warning for warning in result.warnings)

def test_dry_run_validation_api_handler(validator, valid_wpk):
    """Test dry-run validation for API handler"""
    valid_wpk["spec"]["handlers"] = [{
        "name": "api-handler",
        "type": "api",
        "config": {
            "url": "https://external-api.com/delete",
            "method": "DELETE"
        }
    }]
    
    result = validator.dry_run_validation(valid_wpk)
    
    assert result.valid is True
    assert any("External API call detected" in warning for warning in result.warnings)
    assert any("Potentially destructive HTTP method" in warning for warning in result.warnings)

def test_categorize_workflow_manual(validator, valid_wpk):
    """Test workflow categorization as manual"""
    category = validator.categorize_workflow(valid_wpk)
    assert category == "manual"

def test_categorize_workflow_auto_allowed(validator, auto_wpk):
    """Test workflow categorization as auto (when allowed)"""
    # Modify to be low-risk auto workflow
    auto_wpk["spec"]["handlers"][0]["config"]["namespace"] = "development"
    auto_wpk["spec"]["handlers"][0]["config"]["replicas"] = 2
    
    category = validator.categorize_workflow(auto_wpk)
    # Should be downgraded to manual due to approval requirement
    assert category == "manual"

def test_generate_approval_request(validator, auto_wpk):
    """Test approval request generation"""
    # Change to development namespace to trigger approval requirement
    auto_wpk["spec"]["handlers"][0]["config"]["namespace"] = "development"
    
    validation_result = validator.validate_policies(auto_wpk)
    approval_request = validator.generate_approval_request(auto_wpk, validation_result)
    
    assert approval_request["workflow_id"] == "auto-workflow-1.0.0"
    assert approval_request["workflow_name"] == "auto-workflow"
    assert approval_request["safety_mode"] == "auto"
    assert approval_request["status"] == "pending"
    assert approval_request["risk_score"] > 0

def test_policy_engine_safety_policy(policy_engine, auto_wpk):
    """Test safety policy evaluation"""
    decision, reasons = policy_engine.evaluate_safety_policy(auto_wpk)
    
    assert decision == PolicyDecision.DENY
    assert any("Auto mode denied for namespace: production" in reason for reason in reasons)

def test_policy_engine_resource_policy(policy_engine, valid_wpk):
    """Test resource policy evaluation"""
    # Add excessive replicas
    valid_wpk["spec"]["handlers"][0]["config"]["replicas"] = 100
    
    decision, reasons = policy_engine.evaluate_resource_policy(valid_wpk)
    
    assert decision == PolicyDecision.DENY
    assert any("Replica count 100 exceeds limit" in reason for reason in reasons)

def test_policy_engine_security_policy(policy_engine, valid_wpk):
    """Test security policy evaluation"""
    decision, reasons = policy_engine.evaluate_security_policy(valid_wpk)
    
    assert decision == PolicyDecision.ALLOW
    assert len(reasons) == 0

def test_policy_engine_operational_policy(policy_engine, valid_wpk):
    """Test operational policy evaluation"""
    decision, reasons = policy_engine.evaluate_operational_policy(valid_wpk)
    
    assert decision == PolicyDecision.ALLOW
    assert len(reasons) == 0

def test_risk_score_calculation(policy_engine, valid_wpk):
    """Test risk score calculation"""
    risk_score = policy_engine._calculate_risk_score(valid_wpk)
    
    assert risk_score > 0
    assert isinstance(risk_score, int)

def test_risk_score_high_risk(policy_engine, valid_wpk):
    """Test high risk score calculation"""
    # Add multiple risky handlers
    valid_wpk["spec"]["handlers"] = [
        {"name": "shell1", "type": "shell", "config": {}},
        {"name": "shell2", "type": "shell", "config": {}},
        {"name": "shell3", "type": "shell", "config": {}},
        {"name": "api1", "type": "api", "config": {}},
    ]
    valid_wpk["spec"]["safety"]["mode"] = "auto"
    valid_wpk["spec"]["rollback"]["enabled"] = False
    
    risk_score = policy_engine._calculate_risk_score(valid_wpk)
    
    assert risk_score > 10  # Should be high risk

def test_validation_result_creation():
    """Test ValidationResult creation"""
    result = ValidationResult(True, ["error1"], ["warning1"])
    
    assert result.valid is True
    assert result.errors == ["error1"]
    assert result.warnings == ["warning1"]
    assert result.policy_decision == PolicyDecision.ALLOW
    assert result.approval_required is False
    assert result.risk_score == 0

if __name__ == "__main__":
    pytest.main([__file__])