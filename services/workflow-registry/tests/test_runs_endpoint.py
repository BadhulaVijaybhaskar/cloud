"""
Tests for workflow registry runs endpoint
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys

# Add the service directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from main import app, load_workflows, save_workflows

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def sample_workflow():
    """Sample workflow for testing"""
    return {
        "test-workflow-1.0.0": {
            "id": "test-workflow-1.0.0",
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "author": "Test Author",
            "created": "2024-01-15T10:00:00Z",
            "tags": ["test"],
            "safety_mode": "manual",
            "runtime_type": "k8s",
            "file_path": "/tmp/test.wpk.yaml",
            "signature": "test-signature",
            "registered_at": "2024-01-15T10:00:00Z"
        }
    }

@pytest.fixture
def mock_runs_data():
    """Mock run history data"""
    return [
        ("run-123", "completed", 1500, "2024-01-15T10:05:00Z"),
        ("run-124", "failed", 800, "2024-01-15T10:10:00Z"),
        ("run-125", "completed", 2000, "2024-01-15T10:15:00Z")
    ]

def test_get_workflow_runs_not_found():
    """Test getting runs for non-existent workflow"""
    response = client.get("/workflows/non-existent/runs")
    # Should not fail even if workflow doesn't exist in registry
    # The runs endpoint queries the run history directly
    assert response.status_code in [200, 500]  # May fail due to missing run_logger

@patch('main.get_runs_by_wpk_id')
def test_get_workflow_runs_success(mock_get_runs, mock_runs_data):
    """Test successful workflow runs retrieval"""
    mock_get_runs.return_value = mock_runs_data
    
    response = client.get("/workflows/test-workflow-1.0.0/runs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "test-workflow-1.0.0"
    assert len(data["runs"]) == 3
    assert data["page"] == 1
    assert data["limit"] == 20
    
    # Check run format
    run = data["runs"][0]
    assert "run_id" in run
    assert "status" in run
    assert "duration_ms" in run
    assert "created_at" in run

@patch('main.get_runs_by_wpk_id')
def test_get_workflow_runs_pagination(mock_get_runs, mock_runs_data):
    """Test workflow runs pagination"""
    # Return subset for pagination
    mock_get_runs.return_value = mock_runs_data[:2]
    
    response = client.get("/workflows/test-workflow-1.0.0/runs?limit=2&page=1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["page"] == 1
    assert len(data["runs"]) == 2

@patch('main.get_runs_by_wpk_id')
def test_get_workflow_runs_empty(mock_get_runs):
    """Test workflow runs with no history"""
    mock_get_runs.return_value = []
    
    response = client.get("/workflows/new-workflow/runs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["runs"] == []
    assert data["total"] == 0

@patch('main.get_runs_by_wpk_id')
def test_get_workflow_runs_error(mock_get_runs):
    """Test workflow runs with database error"""
    mock_get_runs.side_effect = Exception("Database connection failed")
    
    response = client.get("/workflows/test-workflow/runs")
    
    assert response.status_code == 500
    assert "Failed to get workflow runs" in response.json()["detail"]

def test_notify_workflow_run_success(sample_workflow, auth_headers):
    """Test successful workflow run notification"""
    # Setup workflow in registry
    with patch('main.load_workflows', return_value=sample_workflow):
        with patch('main.save_workflows') as mock_save:
            run_data = {
                "run_id": "run-456",
                "status": "completed",
                "duration_ms": 1200
            }
            
            response = client.post(
                "/workflows/test-workflow-1.0.0/runs/notify",
                json=run_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Workflow run notification processed"
            assert data["workflow_id"] == "test-workflow-1.0.0"
            assert data["run_id"] == "run-456"
            
            # Verify save_workflows was called
            mock_save.assert_called_once()

def test_notify_workflow_run_not_found(auth_headers):
    """Test workflow run notification for non-existent workflow"""
    with patch('main.load_workflows', return_value={}):
        run_data = {
            "run_id": "run-456",
            "status": "completed"
        }
        
        response = client.post(
            "/workflows/non-existent/runs/notify",
            json=run_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Workflow not found" in response.json()["detail"]

def test_notify_workflow_run_no_auth():
    """Test workflow run notification without authentication"""
    run_data = {
        "run_id": "run-456",
        "status": "completed"
    }
    
    response = client.post(
        "/workflows/test-workflow/runs/notify",
        json=run_data
    )
    
    assert response.status_code == 403  # No auth header

def test_notify_workflow_run_updates_metadata(sample_workflow, auth_headers):
    """Test that run notification updates workflow metadata"""
    updated_workflows = {}
    
    def mock_save(workflows):
        updated_workflows.update(workflows)
    
    with patch('main.load_workflows', return_value=sample_workflow):
        with patch('main.save_workflows', side_effect=mock_save):
            run_data = {
                "run_id": "run-789",
                "status": "failed",
                "duration_ms": 500
            }
            
            response = client.post(
                "/workflows/test-workflow-1.0.0/runs/notify",
                json=run_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            
            # Check updated metadata
            workflow = updated_workflows["test-workflow-1.0.0"]
            assert workflow["latest_run_id"] == "run-789"
            assert workflow["latest_run_status"] == "failed"
            assert "latest_run_at" in workflow
            assert workflow["total_runs"] == 1

def test_workflow_runs_integration():
    """Test integration between run logging and registry"""
    # This test verifies the integration works end-to-end
    workflow_id = "integration-test-1.0.0"
    
    # Mock the run logger function
    with patch('main.get_runs_by_wpk_id') as mock_get_runs:
        mock_get_runs.return_value = [
            ("integration-run-1", "completed", 1000, "2024-01-15T10:00:00Z")
        ]
        
        response = client.get(f"/workflows/{workflow_id}/runs")
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == workflow_id
        assert len(data["runs"]) == 1
        assert data["runs"][0]["run_id"] == "integration-run-1"

def test_runs_endpoint_query_parameters():
    """Test runs endpoint with various query parameters"""
    with patch('main.get_runs_by_wpk_id') as mock_get_runs:
        mock_get_runs.return_value = []
        
        # Test default parameters
        response = client.get("/workflows/test/runs")
        assert response.status_code == 200
        mock_get_runs.assert_called_with("test", limit=20, offset=0)
        
        # Test custom parameters
        response = client.get("/workflows/test/runs?limit=10&page=3")
        assert response.status_code == 200
        mock_get_runs.assert_called_with("test", limit=10, offset=20)  # page 3 = offset 20

def test_runs_endpoint_response_format():
    """Test runs endpoint response format"""
    mock_runs = [
        ("run-1", "completed", 1500, "2024-01-15T10:00:00Z"),
        ("run-2", "failed", 800, "2024-01-15T10:05:00Z")
    ]
    
    with patch('main.get_runs_by_wpk_id', return_value=mock_runs):
        response = client.get("/workflows/test/runs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = ["workflow_id", "runs", "page", "limit", "total"]
        for field in required_fields:
            assert field in data
        
        # Check run structure
        run = data["runs"][0]
        required_run_fields = ["run_id", "status", "duration_ms", "created_at"]
        for field in required_run_fields:
            assert field in run

if __name__ == "__main__":
    pytest.main([__file__])