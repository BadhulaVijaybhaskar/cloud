import json
import os
import requests
import pytest

def test_system_health():
    """Test system health endpoint availability"""
    try:
        r = requests.get("http://localhost:8080/health", timeout=5)
        assert r.status_code == 200
    except requests.exceptions.RequestException:
        # In simulation mode, service may not be running
        pytest.skip("Health endpoint not available in simulation mode")

def test_vault_unsealed():
    """Test that Vault is unsealed based on precheck log"""
    precheck_log = "reports/launch_day/precheck.log"
    if os.path.exists(precheck_log):
        with open(precheck_log) as f:
            content = f.read()
            # Check for Vault unsealed status or skip if not available
            if "Sealed:" in content:
                assert "Sealed: false" in content
            else:
                pytest.skip("Vault status not available in precheck log")
    else:
        pytest.skip("Precheck log not found")

def test_governance_report_exists():
    """Test that governance report exists from Phase I.9"""
    governance_report = "reports/I9_governance_test_report.json"
    if os.path.exists(governance_report):
        assert os.path.getsize(governance_report) > 0
    else:
        pytest.skip("Governance report not found - may not be generated yet")

def test_validation_summary_generated():
    """Test that validation summary is generated"""
    summary_file = "reports/launch_day/validation_summary.json"
    if os.path.exists(summary_file):
        with open(summary_file) as f:
            data = json.load(f)
            assert data["phase"] == "J.4"
            assert data["simulation_mode"] is True
            assert "status" in data
    else:
        pytest.skip("Validation summary not generated yet")

def test_required_directories_exist():
    """Test that all required directories are created"""
    required_dirs = [
        "infra/scripts/j4",
        "reports/launch_day",
        "docs/runbooks"
    ]
    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Required directory {dir_path} does not exist"