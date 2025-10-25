import pytest
import yaml
import jsonschema
from pathlib import Path

def load_wpk_schema():
    """Load WPK schema for validation"""
    schema = {
        "type": "object",
        "required": ["apiVersion", "kind", "metadata", "spec"],
        "properties": {
            "apiVersion": {"type": "string", "enum": ["v1"]},
            "kind": {"type": "string", "enum": ["WorkflowPackage"]},
            "metadata": {
                "type": "object",
                "required": ["name", "version", "description", "author"],
                "properties": {
                    "name": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
                    "description": {"type": "string"},
                    "author": {"type": "string"},
                    "created": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "signature": {"type": "string"}
                }
            },
            "spec": {
                "type": "object",
                "required": ["runtime", "safety", "handlers"],
                "properties": {
                    "runtime": {
                        "type": "object",
                        "required": ["type"],
                        "properties": {
                            "type": {"type": "string", "enum": ["k8s", "docker", "shell"]},
                            "version": {"type": "string"},
                            "requirements": {"type": "object"}
                        }
                    },
                    "safety": {
                        "type": "object",
                        "required": ["mode"],
                        "properties": {
                            "mode": {"type": "string", "enum": ["manual", "auto"]},
                            "approval_required": {"type": "boolean"},
                            "dry_run_required": {"type": "boolean"},
                            "rollback_enabled": {"type": "boolean"}
                        }
                    },
                    "handlers": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["name", "type", "config"],
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "config": {"type": "object"},
                                "timeout": {"type": "string"},
                                "retry": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    }
    return schema

def test_wpk_schema_validation():
    """Test WPK schema validation"""
    schema = load_wpk_schema()
    
    # Test valid WPK
    valid_wpk = {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "author": "Test Author"
        },
        "spec": {
            "runtime": {"type": "k8s"},
            "safety": {"mode": "manual"},
            "handlers": [
                {
                    "name": "test-handler",
                    "type": "k8s",
                    "config": {"action": "test"}
                }
            ]
        }
    }
    
    # Should not raise exception
    jsonschema.validate(valid_wpk, schema)

def test_restart_unhealthy_wpk():
    """Test the restart-unhealthy example WPK"""
    wpk_path = Path(__file__).parent.parent.parent / "examples" / "playbooks" / "restart-unhealthy.wpk.yaml"
    
    with open(wpk_path, 'r') as f:
        wpk_data = yaml.safe_load(f)
    
    schema = load_wpk_schema()
    
    # Should not raise exception
    jsonschema.validate(wpk_data, schema)
    
    # Additional checks
    assert wpk_data["metadata"]["name"] == "restart-unhealthy"
    assert wpk_data["spec"]["safety"]["mode"] == "manual"
    assert len(wpk_data["spec"]["handlers"]) == 4

def test_invalid_wpk_missing_required():
    """Test validation fails for missing required fields"""
    schema = load_wpk_schema()
    
    invalid_wpk = {
        "apiVersion": "v1",
        "kind": "WorkflowPackage"
        # Missing metadata and spec
    }
    
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid_wpk, schema)

def test_invalid_safety_mode():
    """Test validation fails for invalid safety mode"""
    schema = load_wpk_schema()
    
    invalid_wpk = {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "author": "Test Author"
        },
        "spec": {
            "runtime": {"type": "k8s"},
            "safety": {"mode": "invalid"},  # Invalid mode
            "handlers": [
                {
                    "name": "test-handler",
                    "type": "k8s",
                    "config": {"action": "test"}
                }
            ]
        }
    }
    
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid_wpk, schema)

if __name__ == "__main__":
    pytest.main([__file__])