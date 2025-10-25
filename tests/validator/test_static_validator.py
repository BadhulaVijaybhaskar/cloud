"""
Tests for static validator functionality.
"""

import pytest
import sys
from pathlib import Path

# Add validator to path
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "workflow-registry" / "validator"))

from static_validator import StaticValidator, ValidationIssue, Severity, ValidationResult

class TestStaticValidator:
    """Test static validator functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.validator = StaticValidator()
        
        # Sample unsafe WPK
        self.unsafe_wpk = {
            "apiVersion": "v1",
            "kind": "WorkflowPackage",
            "metadata": {"name": "unsafe-workflow", "version": "1.0.0"},
            "spec": {
                "runtime": {"type": "kubernetes"},
                "safety": {"mode": "auto"},
                "handlers": [{
                    "name": "unsafe-handler",
                    "steps": [{
                        "name": "privileged-container",
                        "container": {
                            "image": "ubuntu:latest",
                            "securityContext": {
                                "privileged": True,
                                "capabilities": {"add": ["CAP_SYS_ADMIN"]}
                            },
                            "volumeMounts": [{"name": "host-root", "mountPath": "/"}],
                            "resources": {"limits": {"cpu": "8", "memory": "16Gi"}}
                        }
                    }]
                }]
            }
        }
        
        # Sample safe WPK
        self.safe_wpk = {
            "apiVersion": "v1",
            "kind": "WorkflowPackage",
            "metadata": {"name": "safe-workflow", "version": "1.0.0"},
            "spec": {
                "runtime": {"type": "kubernetes"},
                "safety": {"mode": "manual"},
                "handlers": [{
                    "name": "safe-handler",
                    "steps": [{
                        "name": "safe-container",
                        "container": {
                            "image": "ubuntu:20.04",
                            "resources": {
                                "limits": {"cpu": "500m", "memory": "512Mi"}
                            }
                        }
                    }]
                }]
            }
        }
    
    def test_validate_safe_wpk(self):
        """Test validation of safe WPK."""
        result = self.validator.validate(self.safe_wpk)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.risk_score < 50
        assert len(result.critical_issues) == 0
    
    def test_validate_unsafe_wpk(self):
        """Test validation of unsafe WPK."""
        result = self.validator.validate(self.unsafe_wpk)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is False
        assert result.risk_score >= 76
        assert len(result.critical_issues) > 0
    
    def test_privileged_container_detection(self):
        """Test detection of privileged containers."""
        result = self.validator.validate(self.unsafe_wpk)
        
        privileged_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "privileged_container"
        ]
        
        assert len(privileged_issues) > 0
        assert privileged_issues[0].severity == Severity.CRITICAL
    
    def test_sensitive_path_detection(self):
        """Test sensitive path detection."""
        assert self.validator._is_sensitive_path("/") is True
        assert self.validator._is_sensitive_path("/etc") is True
        assert self.validator._is_sensitive_path("/home/user") is False
    
    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        unsafe_result = self.validator.validate(self.unsafe_wpk)
        safe_result = self.validator.validate(self.safe_wpk)
        
        assert unsafe_result.risk_score > safe_result.risk_score

if __name__ == "__main__":
    pytest.main([__file__, "-v"])