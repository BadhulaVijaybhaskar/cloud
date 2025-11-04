import json
import os
import requests
import pytest
from datetime import datetime

def test_required_directories_exist():
    """Test that all required directories for J.5 are created"""
    required_dirs = [
        "infra/scripts/j5",
        "reports/j5",
        "infra/contracts/partners",
        "infra/vault/policies"
    ]
    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Required directory {dir_path} does not exist"

def test_deployment_scripts_exist():
    """Test that deployment scripts are present"""
    scripts = [
        "infra/scripts/j5/run_launch_day.sh",
        "infra/scripts/j5/rollback_prod.sh"
    ]
    for script in scripts:
        assert os.path.exists(script), f"Required script {script} does not exist"
        assert os.path.getsize(script) > 0, f"Script {script} is empty"

def test_checklist_exists():
    """Test that production checklist exists"""
    checklist_path = "docs/checklist_to_run_live.md"
    assert os.path.exists(checklist_path), "Production checklist not found"
    
    with open(checklist_path) as f:
        content = f.read()
        assert "APPROVE_DEPLOY=yes" in content
        assert "Security Admin" in content
        assert "Emergency Contact List" in content

def test_partner_federation_config():
    """Test that partner federation configuration is valid"""
    config_path = "infra/contracts/partners/federation_registry.json"
    assert os.path.exists(config_path), "Partner federation config not found"
    
    with open(config_path) as f:
        config = json.load(f)
        assert "federation_registry" in config
        assert "partners" in config["federation_registry"]
        assert len(config["federation_registry"]["partners"]) > 0

def test_vault_policies_exist():
    """Test that Vault policies are present"""
    policy_path = "infra/vault/policies/production.hcl"
    assert os.path.exists(policy_path), "Production Vault policy not found"
    
    with open(policy_path) as f:
        content = f.read()
        assert "secret/data/database" in content
        assert "secret/data/services" in content
        assert "secret/data/partners" in content

def test_j4_validation_complete():
    """Test that J.4 validation was completed"""
    j4_summary = "reports/launch_day/validation_summary.json"
    if os.path.exists(j4_summary):
        with open(j4_summary) as f:
            data = json.load(f)
            assert data["phase"] == "J.4"
            assert data["status"] == "PASSED"
    else:
        pytest.skip("J.4 validation summary not found")

def test_governance_compliance():
    """Test that governance reports are available"""
    governance_files = [
        "reports/launch_day/governance_report.json",
        "reports/I9_governance_test_report.json"
    ]
    
    found_reports = [f for f in governance_files if os.path.exists(f)]
    assert len(found_reports) > 0, "No governance reports found"

def test_production_environment_variables():
    """Test that production environment variables are documented"""
    # This would typically check environment configuration
    # For now, we verify the scripts reference the correct variables
    script_path = "infra/scripts/j5/run_launch_day.sh"
    with open(script_path) as f:
        content = f.read()
        assert "SIMULATION_MODE" in content
        assert "APPROVE_DEPLOY" in content
        assert "atom-prod" in content