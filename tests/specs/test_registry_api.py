import pytest
import requests
import yaml
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
import sys

# Add the service directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "workflow-registry"))

from main import app

client = TestClient(app)

@pytest.fixture
def sample_wpk():
    """Sample WPK for testing"""
    return {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "Test workflow for registry",
            "author": "Test Author",
            "signature": "test-signature-123"
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

@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test-token"}

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_register_workflow_success(sample_wpk, auth_headers):
    """Test successful workflow registration"""
    wpk_yaml = yaml.dump(sample_wpk)
    
    files = {"file": ("test.wpk.yaml", wpk_yaml, "application/x-yaml")}
    response = client.post("/workflows", files=files, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Workflow registered successfully"
    assert data["workflow_id"] == "test-workflow-1.0.0"
    assert data["status"] == "registered"

def test_register_workflow_invalid_yaml(auth_headers):
    """Test workflow registration with invalid YAML"""
    invalid_yaml = "invalid: yaml: content: ["
    
    files = {"file": ("invalid.wpk.yaml", invalid_yaml, "application/x-yaml")}
    response = client.post("/workflows", files=files, headers=auth_headers)
    
    assert response.status_code == 400
    assert "Invalid YAML format" in response.json()["detail"]

def test_register_workflow_missing_signature(auth_headers):
    """Test workflow registration without signature"""
    wpk_no_sig = {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "no-sig-workflow",
            "version": "1.0.0",
            "description": "Workflow without signature",
            "author": "Test Author"
        },
        "spec": {
            "runtime": {"type": "k8s"},
            "safety": {"mode": "manual"},
            "handlers": [{"name": "test", "type": "k8s", "config": {}}]
        }
    }
    
    wpk_yaml = yaml.dump(wpk_no_sig)
    files = {"file": ("nosig.wpk.yaml", wpk_yaml, "application/x-yaml")}
    response = client.post("/workflows", files=files, headers=auth_headers)
    
    assert response.status_code == 400
    assert "WPK must be signed with cosign" in response.json()["detail"]

def test_list_workflows_empty():
    """Test listing workflows when registry is empty"""
    response = client.get("/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert "total" in data

def test_list_workflows_with_filters():
    """Test listing workflows with filters"""
    # Test with tag filter
    response = client.get("/workflows?tag=kubernetes")
    assert response.status_code == 200
    
    # Test with runtime filter
    response = client.get("/workflows?runtime=k8s")
    assert response.status_code == 200
    
    # Test with safety mode filter
    response = client.get("/workflows?safety_mode=manual")
    assert response.status_code == 200

def test_get_workflow_not_found():
    """Test getting non-existent workflow"""
    response = client.get("/workflows/non-existent-workflow")
    assert response.status_code == 404
    assert "Workflow not found" in response.json()["detail"]

def test_sign_workflow_not_found(auth_headers):
    """Test signing non-existent workflow"""
    response = client.post("/workflows/non-existent/sign", headers=auth_headers)
    assert response.status_code == 404
    assert "Workflow not found" in response.json()["detail"]

def test_delete_workflow_not_found(auth_headers):
    """Test deleting non-existent workflow"""
    response = client.delete("/workflows/non-existent", headers=auth_headers)
    assert response.status_code == 404
    assert "Workflow not found" in response.json()["detail"]

def test_workflow_lifecycle(sample_wpk, auth_headers):
    """Test complete workflow lifecycle: register -> list -> get -> sign -> delete"""
    
    # 1. Register workflow
    wpk_yaml = yaml.dump(sample_wpk)
    files = {"file": ("lifecycle.wpk.yaml", wpk_yaml, "application/x-yaml")}
    response = client.post("/workflows", files=files, headers=auth_headers)
    assert response.status_code == 200
    workflow_id = response.json()["workflow_id"]
    
    # 2. List workflows (should include our workflow)
    response = client.get("/workflows")
    assert response.status_code == 200
    workflows = response.json()["workflows"]
    workflow_names = [w["name"] for w in workflows]
    assert sample_wpk["metadata"]["name"] in workflow_names
    
    # 3. Get specific workflow
    response = client.get(f"/workflows/{workflow_id}")
    assert response.status_code == 200
    workflow_data = response.json()
    assert workflow_data["name"] == sample_wpk["metadata"]["name"]
    assert "wpk_content" in workflow_data
    
    # 4. Sign workflow
    response = client.post(f"/workflows/{workflow_id}/sign", headers=auth_headers)
    assert response.status_code == 200
    assert "signature" in response.json()
    
    # 5. Delete workflow
    response = client.delete(f"/workflows/{workflow_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # 6. Verify deletion
    response = client.get(f"/workflows/{workflow_id}")
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__])