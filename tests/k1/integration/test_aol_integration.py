import json
import os
import requests
import pytest
import time

def test_aol_services_directory_structure():
    """Test that all AOL service directories exist"""
    services = ['aol-controller', 'aol-policy', 'aol-executor', 'aol-simulator']
    for service in services:
        service_dir = f"services/{service}"
        assert os.path.exists(service_dir), f"Service directory {service_dir} not found"
        assert os.path.exists(f"{service_dir}/src"), f"Source directory for {service} not found"
        assert os.path.exists(f"{service_dir}/Dockerfile"), f"Dockerfile for {service} not found"

def test_aol_scripts_exist():
    """Test that AOL management scripts exist"""
    scripts = [
        "infra/scripts/k1/precheck_k1.sh",
        "infra/scripts/k1/activate_aol.sh", 
        "infra/scripts/k1/deactivate_aol.sh"
    ]
    for script in scripts:
        assert os.path.exists(script), f"Script {script} not found"
        assert os.path.getsize(script) > 0, f"Script {script} is empty"

def test_helm_chart_structure():
    """Test that Helm chart structure is correct"""
    chart_files = [
        "infra/helm/aol/Chart.yaml",
        "infra/helm/aol/values.yaml",
        "infra/helm/aol/templates/controller.yaml",
        "infra/helm/aol/templates/policy.yaml"
    ]
    for file_path in chart_files:
        assert os.path.exists(file_path), f"Helm chart file {file_path} not found"

def test_policy_schemas_exist():
    """Test that policy schemas are present"""
    schemas = [
        "services/aol-policy/schemas/decision.json",
        "services/aol-policy/schemas/policy_response.json"
    ]
    for schema in schemas:
        assert os.path.exists(schema), f"Schema {schema} not found"
        
        # Validate JSON schema format
        with open(schema) as f:
            schema_data = json.load(f)
            assert "type" in schema_data, f"Schema {schema} missing type field"

def test_vault_policy_exists():
    """Test that Vault policy for AOL exists"""
    policy_path = "infra/vault/policies/aol.hcl"
    assert os.path.exists(policy_path), "AOL Vault policy not found"
    
    with open(policy_path) as f:
        content = f.read()
        assert "secret/data/aol" in content
        assert "auth/kubernetes/role/aol-controller" in content

def test_aol_controller_health_simulation():
    """Test AOL controller health endpoint (simulation)"""
    # This would test the actual service if running
    # For now, just verify the source code structure
    controller_main = "services/aol-controller/src/main.py"
    with open(controller_main) as f:
        content = f.read()
        assert "/health" in content
        assert "/v1/decide" in content
        assert "SIMULATION_MODE" in content

def test_aol_policy_engine_structure():
    """Test AOL policy engine structure"""
    policy_engine = "services/aol-policy/src/policy_engine.py"
    with open(policy_engine) as f:
        content = f.read()
        assert "/v1/evaluate" in content
        assert "P1-P20" in content
        assert "SAFE_ACTIONS" in content

def test_reports_directory_structure():
    """Test that reports directory structure is ready"""
    reports_dir = "reports/k1"
    assert os.path.exists(reports_dir), "Reports directory for K1 not found"

def test_terraform_module_structure():
    """Test that Terraform module structure exists"""
    tf_module_dir = "infra/terraform/modules/aol"
    assert os.path.exists(tf_module_dir), "Terraform AOL module directory not found"