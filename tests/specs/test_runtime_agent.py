import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the service directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "runtime-agent"))

from main import app, runtime_agent, execution_state

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
            "description": "Test workflow",
            "author": "Test Author"
        },
        "spec": {
            "runtime": {"type": "k8s"},
            "safety": {"mode": "manual"},
            "handlers": [
                {
                    "name": "test-logs",
                    "type": "k8s",
                    "config": {
                        "action": "logs",
                        "resource": "test-pod",
                        "lines": 100
                    }
                },
                {
                    "name": "test-restart",
                    "type": "k8s",
                    "config": {
                        "action": "restart",
                        "resource_type": "deployment",
                        "resource_name": "test-app"
                    }
                }
            ],
            "rollback": {
                "enabled": True,
                "handlers": [
                    {
                        "name": "rollback-restart",
                        "type": "k8s",
                        "config": {
                            "action": "rollback",
                            "resource_type": "deployment"
                        }
                    }
                ]
            }
        }
    }

@pytest.fixture
def execution_request(sample_wpk):
    """Sample execution request"""
    return {
        "workflow_id": "test-workflow-1.0.0",
        "wpk_content": sample_wpk,
        "parameters": {"namespace": "default"},
        "dry_run": False
    }

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "active_executions" in data

def test_initialize_agent():
    """Test agent initialization"""
    response = client.post("/init")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "initialized"
    assert "adapters" in data
    assert "k8s" in data["adapters"]
    assert "shell" in data["adapters"]
    assert "api" in data["adapters"]

def test_validate_workflow_success(execution_request):
    """Test successful workflow validation"""
    response = client.post("/validate", json=execution_request)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "valid"
    assert data["workflow_name"] == "test-workflow"
    assert data["total_handlers"] == 2

def test_validate_workflow_invalid_structure():
    """Test validation with invalid WPK structure"""
    invalid_request = {
        "workflow_id": "invalid",
        "wpk_content": {"invalid": "structure"},
        "parameters": {}
    }
    
    response = client.post("/validate", json=invalid_request)
    assert response.status_code == 400
    assert "Invalid WPK structure" in response.json()["detail"]

def test_validate_workflow_no_handlers():
    """Test validation with no handlers"""
    no_handlers_request = {
        "workflow_id": "no-handlers",
        "wpk_content": {
            "metadata": {"name": "test"},
            "spec": {}  # No handlers
        },
        "parameters": {}
    }
    
    response = client.post("/validate", json=no_handlers_request)
    assert response.status_code == 400
    assert "No handlers defined" in response.json()["detail"]

def test_validate_workflow_unknown_handler():
    """Test validation with unknown handler type"""
    unknown_handler_request = {
        "workflow_id": "unknown-handler",
        "wpk_content": {
            "metadata": {"name": "test"},
            "spec": {
                "handlers": [
                    {
                        "name": "unknown",
                        "type": "unknown_type",
                        "config": {}
                    }
                ]
            }
        },
        "parameters": {}
    }
    
    response = client.post("/validate", json=unknown_handler_request)
    assert response.status_code == 400
    assert "Unknown handler type" in response.json()["detail"]

def test_execute_workflow(execution_request):
    """Test workflow execution"""
    response = client.post("/execute", json=execution_request)
    assert response.status_code == 200
    data = response.json()
    assert "execution_id" in data
    assert data["status"] == "started"
    
    execution_id = data["execution_id"]
    
    # Check execution was created
    assert execution_id in execution_state
    assert execution_state[execution_id]["workflow_id"] == execution_request["workflow_id"]

def test_get_execution_status(execution_request):
    """Test getting execution status"""
    # Start execution
    response = client.post("/execute", json=execution_request)
    execution_id = response.json()["execution_id"]
    
    # Get status
    response = client.get(f"/execute/{execution_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["execution_id"] == execution_id
    assert "status" in data
    assert "logs" in data

def test_get_execution_status_not_found():
    """Test getting status for non-existent execution"""
    response = client.get("/execute/non-existent-id")
    assert response.status_code == 404
    assert "Execution not found" in response.json()["detail"]

def test_get_execution_logs(execution_request):
    """Test getting execution logs"""
    # Start execution
    response = client.post("/execute", json=execution_request)
    execution_id = response.json()["execution_id"]
    
    # Get logs
    response = client.get(f"/logs/{execution_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["execution_id"] == execution_id
    assert "logs" in data

def test_get_execution_logs_not_found():
    """Test getting logs for non-existent execution"""
    response = client.get("/logs/non-existent-id")
    assert response.status_code == 404
    assert "Execution not found" in response.json()["detail"]

def test_rollback_execution_not_found():
    """Test rollback for non-existent execution"""
    response = client.post("/rollback/non-existent-id")
    assert response.status_code == 404
    assert "Execution not found" in response.json()["detail"]

def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Check for some expected metrics
    content = response.content.decode()
    assert "workflow_runs_total" in content
    assert "workflow_duration_seconds" in content

def test_dry_run_execution(execution_request):
    """Test dry run execution"""
    execution_request["dry_run"] = True
    
    response = client.post("/execute", json=execution_request)
    assert response.status_code == 200
    data = response.json()
    assert "execution_id" in data
    
    execution_id = data["execution_id"]
    
    # Wait a bit for background task
    import time
    time.sleep(0.5)
    
    # Check execution status
    response = client.get(f"/execute/{execution_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_k8s_adapter():
    """Test k8s adapter functionality"""
    # Test logs action
    result = await runtime_agent.k8s_adapter("logs", {"resource": "test-pod", "lines": 100})
    assert result["status"] == "success"
    assert result["action"] == "logs"
    
    # Test restart action
    result = await runtime_agent.k8s_adapter("restart", {"resource_type": "deployment", "resource_name": "test-app"})
    assert result["status"] == "success"
    assert result["action"] == "restart"
    
    # Test dry run
    result = await runtime_agent.k8s_adapter("logs", {"resource": "test-pod"}, dry_run=True)
    assert result["status"] == "success"
    assert result["dry_run"] is True

@pytest.mark.asyncio
async def test_shell_adapter():
    """Test shell adapter functionality"""
    result = await runtime_agent.shell_adapter("echo 'test'", {})
    assert result["status"] == "success"
    assert "returncode" in result
    
    # Test dry run
    result = await runtime_agent.shell_adapter("echo 'test'", {}, dry_run=True)
    assert result["status"] == "success"
    assert result["dry_run"] is True

@pytest.mark.asyncio
async def test_api_adapter():
    """Test API adapter functionality"""
    result = await runtime_agent.api_adapter("http://example.com", {"method": "GET"})
    assert result["status"] == "success"
    assert "response_code" in result
    
    # Test dry run
    result = await runtime_agent.api_adapter("http://example.com", {"method": "POST"}, dry_run=True)
    assert result["status"] == "success"
    assert result["dry_run"] is True

if __name__ == "__main__":
    pytest.main([__file__])