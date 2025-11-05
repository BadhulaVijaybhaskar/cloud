import os
import json
import pytest

def test_k5_reports_exist():
    """Test that K5 reports are generated correctly"""
    root = "."
    rpt = os.path.join(root, "reports/k5")
    assert os.path.exists(rpt), "K5 reports directory should exist"
    
    for f in ["precheck_report.json", "deploy_summary.json", "verification_summary.json"]:
        p = os.path.join(rpt, f)
        assert os.path.exists(p), f"Report {f} should exist"
        with open(p) as fh:
            data = json.load(fh)
            assert data.get("phase") == "K.5", f"Report {f} should be for K.5 phase"
            assert data.get("simulation_mode") is True, f"Report {f} should be in simulation mode"

def test_explainability_artifacts():
    """Test that explainability artifacts are created"""
    explainability_dir = os.path.join("reports/k5/explainability_reports")
    assert os.path.exists(explainability_dir), "Explainability reports directory should exist"
    
    # Check for at least one explainability artifact
    artifacts = [f for f in os.listdir(explainability_dir) if f.endswith('.json')]
    assert len(artifacts) > 0, "At least one explainability artifact should exist"
    
    # Validate artifact structure
    with open(os.path.join(explainability_dir, artifacts[0])) as f:
        artifact = json.load(f)
        assert "id" in artifact, "Explainability artifact should have ID"
        assert "top_features" in artifact, "Explainability artifact should have top features"
        assert "importance" in artifact, "Explainability artifact should have importance scores"

def test_service_directories():
    """Test that all K5 service directories exist"""
    services = [
        "services/meta-learner",
        "services/explainability-engine", 
        "services/policy-refiner",
        "services/autonomy-auditor",
        "services/simulator-proxy"
    ]
    
    for service in services:
        assert os.path.exists(service), f"Service directory {service} should exist"
        main_py = os.path.join(service, "src/main.py")
        assert os.path.exists(main_py), f"Service {service} should have main.py"

def test_infrastructure_files():
    """Test that infrastructure files exist"""
    infra_files = [
        "infra/terraform/modules/k5_full_autonomy/main.tf",
        "infra/helm/k5-full-autonomy/Chart.yaml",
        "infra/helm/k5-full-autonomy/values.yaml",
        "infra/vault/policies/k5_full_autonomy.hcl"
    ]
    
    for file_path in infra_files:
        assert os.path.exists(file_path), f"Infrastructure file {file_path} should exist"

def test_scripts_executable():
    """Test that K5 scripts exist"""
    scripts = [
        "infra/scripts/k5/precheck.sh",
        "infra/scripts/k5/deploy.sh", 
        "infra/scripts/k5/verify.sh"
    ]
    
    for script in scripts:
        assert os.path.exists(script), f"Script {script} should exist"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])