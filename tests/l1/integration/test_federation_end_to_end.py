import os
import json
import pytest

def test_l1_reports_exist():
    """Test that L1 federation reports are generated correctly"""
    rpt = "reports/l1"
    assert os.path.exists(rpt), "L1 reports directory should exist"
    
    for f in ["precheck_report.json", "deploy_summary.json", "verification_summary.json", "federation_health.json"]:
        p = os.path.join(rpt, f)
        assert os.path.exists(p), f"Report {f} should exist"
        with open(p) as fh:
            data = json.load(fh)
            assert data.get("phase") == "L.1" or "federation" in str(data), f"Report {f} should be for L.1 phase"

def test_federation_services_exist():
    """Test that all L1 federation service directories exist"""
    services = [
        "services/federation-orchestrator",
        "services/federation-gateway", 
        "services/federation-metadata",
        "services/federation-policy-broker",
        "services/federation-mirror-agent"
    ]
    
    for service in services:
        assert os.path.exists(service), f"Service directory {service} should exist"
        main_py = os.path.join(service, "src/main.py")
        assert os.path.exists(main_py), f"Service {service} should have main.py"

def test_infrastructure_files():
    """Test that infrastructure files exist"""
    infra_files = [
        "infra/terraform/modules/l1_federation/main.tf",
        "infra/helm/l1-federation/Chart.yaml",
        "infra/helm/l1-federation/values.yaml",
        "infra/vault/policies/l1_federation.hcl"
    ]
    
    for file_path in infra_files:
        assert os.path.exists(file_path), f"Infrastructure file {file_path} should exist"

def test_scripts_exist():
    """Test that L1 scripts exist"""
    scripts = [
        "infra/scripts/l1/precheck.sh",
        "infra/scripts/l1/deploy.sh", 
        "infra/scripts/l1/verify.sh"
    ]
    
    for script in scripts:
        assert os.path.exists(script), f"Script {script} should exist"

def test_federation_health_structure():
    """Test federation health report structure"""
    health_file = "reports/l1/federation_health.json"
    if os.path.exists(health_file):
        with open(health_file) as f:
            health_data = json.load(f)
            assert "nodes_registered" in health_data, "Health report should have nodes_registered"
            assert "nodes_opted_in" in health_data, "Health report should have nodes_opted_in"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])