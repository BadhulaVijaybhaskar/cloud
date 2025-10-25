import pytest
import asyncio
import json
import yaml
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the adapter directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "adapters" / "k8s_adapter"))

from adapter import KubernetesAdapter, create_k8s_adapter

@pytest.fixture
def k8s_adapter():
    """Create K8s adapter instance for testing"""
    return KubernetesAdapter(namespace="test-namespace")

@pytest.fixture
def mock_execute_command():
    """Mock execute_command method"""
    async def mock_cmd(command, timeout=300):
        if "apply" in command:
            return {
                "returncode": 0,
                "stdout": "configmap/test-configmap created",
                "stderr": "",
                "success": True
            }
        elif "scale" in command:
            return {
                "returncode": 0,
                "stdout": "deployment.apps/test-deployment scaled",
                "stderr": "",
                "success": True
            }
        elif "rollout restart" in command:
            return {
                "returncode": 0,
                "stdout": "deployment.apps/test-deployment restarted",
                "stderr": "",
                "success": True
            }
        elif "rollout status" in command:
            return {
                "returncode": 0,
                "stdout": "deployment \"test-deployment\" successfully rolled out",
                "stderr": "",
                "success": True
            }
        elif "wait" in command and "condition=available" in command:
            return {
                "returncode": 0,
                "stdout": "deployment.apps/test-deployment condition met",
                "stderr": "",
                "success": True
            }
        elif "wait" in command and "condition=complete" in command:
            return {
                "returncode": 0,
                "stdout": "job.batch/test-job condition met",
                "stderr": "",
                "success": True
            }
        elif "get pods" in command and "job-name" in command:
            return {
                "returncode": 0,
                "stdout": "test-job-pod-123",
                "stderr": "",
                "success": True
            }
        elif "logs" in command:
            return {
                "returncode": 0,
                "stdout": "Hello from test job!",
                "stderr": "",
                "success": True
            }
        elif "get" in command and "-o json" in command:
            return {
                "returncode": 0,
                "stdout": json.dumps({
                    "metadata": {"name": "test-deployment"},
                    "status": {"readyReplicas": 2}
                }),
                "stderr": "",
                "success": True
            }
        elif "rollout undo" in command:
            return {
                "returncode": 0,
                "stdout": "deployment.apps/test-deployment rolled back",
                "stderr": "",
                "success": True
            }
        else:
            return {
                "returncode": 0,
                "stdout": "mock command executed",
                "stderr": "",
                "success": True
            }
    
    return mock_cmd

def test_adapter_initialization():
    """Test adapter initialization"""
    adapter = KubernetesAdapter(namespace="test-ns")
    assert adapter.namespace == "test-ns"
    assert "kubectl" in adapter.kubectl_cmd

def test_create_k8s_adapter():
    """Test factory function"""
    adapter = create_k8s_adapter(namespace="factory-test")
    assert isinstance(adapter, KubernetesAdapter)
    assert adapter.namespace == "factory-test"

@pytest.mark.asyncio
async def test_apply_manifest(k8s_adapter, mock_execute_command):
    """Test applying Kubernetes manifest"""
    k8s_adapter.execute_command = mock_execute_command
    
    manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": "test-configmap",
            "namespace": "test-namespace"
        },
        "data": {
            "key": "value"
        }
    }
    
    result = await k8s_adapter.apply_manifest(manifest)
    
    assert result["status"] == "success"
    assert result["action"] == "apply_manifest"
    assert "successfully" in result["message"]
    assert result["resource"] == "test-configmap"

@pytest.mark.asyncio
async def test_scale_deployment(k8s_adapter, mock_execute_command):
    """Test scaling deployment"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.scale_deployment("test-deployment", replicas=3)
    
    assert result["status"] == "success"
    assert result["action"] == "scale_deployment"
    assert result["deployment"] == "test-deployment"
    assert result["replicas"] == 3
    assert result["namespace"] == "test-namespace"

@pytest.mark.asyncio
async def test_restart_deployment(k8s_adapter, mock_execute_command):
    """Test restarting deployment"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.restart_pod(deployment_name="test-deployment")
    
    assert result["status"] == "success"
    assert result["action"] == "restart_deployment"
    assert result["deployment"] == "test-deployment"

@pytest.mark.asyncio
async def test_restart_pod(k8s_adapter, mock_execute_command):
    """Test restarting specific pod"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.restart_pod(pod_name="test-pod")
    
    assert result["status"] == "success"
    assert result["action"] == "restart_pod"
    assert result["pod"] == "test-pod"

@pytest.mark.asyncio
async def test_restart_no_target(k8s_adapter):
    """Test restart with no pod or deployment specified"""
    result = await k8s_adapter.restart_pod()
    
    assert result["status"] == "error"
    assert "must be specified" in result["message"]

@pytest.mark.asyncio
async def test_run_job_with_completion(k8s_adapter, mock_execute_command):
    """Test running job and waiting for completion"""
    k8s_adapter.execute_command = mock_execute_command
    
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": "test-job",
            "namespace": "test-namespace"
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "test-container",
                            "image": "busybox",
                            "command": ["echo", "hello"]
                        }
                    ],
                    "restartPolicy": "Never"
                }
            }
        }
    }
    
    result = await k8s_adapter.run_job(job_manifest, wait_for_completion=True)
    
    assert result["status"] == "success"
    assert result["action"] == "run_job"
    assert result["job"] == "test-job"
    assert "logs" in result

@pytest.mark.asyncio
async def test_run_job_without_waiting(k8s_adapter, mock_execute_command):
    """Test running job without waiting for completion"""
    k8s_adapter.execute_command = mock_execute_command
    
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": "test-job"},
        "spec": {"template": {"spec": {"containers": []}}}
    }
    
    result = await k8s_adapter.run_job(job_manifest, wait_for_completion=False)
    
    assert result["status"] == "success"
    assert result["action"] == "run_job"
    assert "started" in result["message"]

@pytest.mark.asyncio
async def test_rollback_deployment(k8s_adapter, mock_execute_command):
    """Test rolling back deployment"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.rollback_deployment("test-deployment")
    
    assert result["status"] == "success"
    assert result["action"] == "rollback_deployment"
    assert result["deployment"] == "test-deployment"
    assert result["revision"] == "previous"

@pytest.mark.asyncio
async def test_rollback_deployment_specific_revision(k8s_adapter, mock_execute_command):
    """Test rolling back to specific revision"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.rollback_deployment("test-deployment", revision="2")
    
    assert result["status"] == "success"
    assert result["revision"] == "2"

@pytest.mark.asyncio
async def test_wait_for_deployment_ready(k8s_adapter, mock_execute_command):
    """Test waiting for deployment to be ready"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.wait_for_deployment_ready("test-deployment")
    
    assert result["status"] == "success"
    assert result["action"] == "wait_for_deployment_ready"
    assert result["deployment"] == "test-deployment"

@pytest.mark.asyncio
async def test_wait_for_rollout_complete(k8s_adapter, mock_execute_command):
    """Test waiting for rollout to complete"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.wait_for_rollout_complete("test-deployment")
    
    assert result["status"] == "success"
    assert result["action"] == "wait_for_rollout_complete"

@pytest.mark.asyncio
async def test_wait_for_job_completion(k8s_adapter, mock_execute_command):
    """Test waiting for job completion"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.wait_for_job_completion("test-job")
    
    assert result["status"] == "success"
    assert result["action"] == "wait_for_job_completion"
    assert result["job"] == "test-job"

@pytest.mark.asyncio
async def test_get_job_logs(k8s_adapter, mock_execute_command):
    """Test getting job logs"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.get_job_logs("test-job")
    
    assert result["status"] == "success"
    assert result["action"] == "get_job_logs"
    assert "logs" in result
    assert "Hello from test job!" in result["logs"]

@pytest.mark.asyncio
async def test_get_resource_status(k8s_adapter, mock_execute_command):
    """Test getting resource status"""
    k8s_adapter.execute_command = mock_execute_command
    
    result = await k8s_adapter.get_resource_status("deployment", "test-deployment")
    
    assert result["status"] == "success"
    assert result["action"] == "get_resource_status"
    assert "resource_data" in result
    assert result["resource_data"]["metadata"]["name"] == "test-deployment"

@pytest.mark.asyncio
async def test_execute_command_timeout():
    """Test command execution timeout"""
    adapter = KubernetesAdapter()
    
    # Mock asyncio.create_subprocess_shell to simulate timeout
    with patch('asyncio.create_subprocess_shell') as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"output", b"error")
        mock_subprocess.return_value = mock_process
        
        # Mock asyncio.wait_for to raise TimeoutError
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            result = await adapter.execute_command("sleep 1000", timeout=1)
            
            assert result["returncode"] == 124
            assert "timed out" in result["stderr"]
            assert not result["success"]

@pytest.mark.asyncio
async def test_execute_command_exception():
    """Test command execution with exception"""
    adapter = KubernetesAdapter()
    
    # Mock asyncio.create_subprocess_shell to raise exception
    with patch('asyncio.create_subprocess_shell', side_effect=Exception("Test error")):
        result = await adapter.execute_command("invalid-command")
        
        assert result["returncode"] == 1
        assert "Test error" in result["stderr"]
        assert not result["success"]

@pytest.mark.asyncio
async def test_apply_manifest_failure(k8s_adapter):
    """Test apply manifest failure"""
    # Mock execute_command to return failure
    async def mock_fail_cmd(command, timeout=300):
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "error: unable to apply manifest",
            "success": False
        }
    
    k8s_adapter.execute_command = mock_fail_cmd
    
    manifest = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "test"}}
    result = await k8s_adapter.apply_manifest(manifest)
    
    assert result["status"] == "error"
    assert "Failed to apply manifest" in result["message"]

@pytest.mark.asyncio
async def test_scale_deployment_failure(k8s_adapter):
    """Test scale deployment failure"""
    # Mock execute_command to return failure
    async def mock_fail_cmd(command, timeout=300):
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "error: deployment not found",
            "success": False
        }
    
    k8s_adapter.execute_command = mock_fail_cmd
    
    result = await k8s_adapter.scale_deployment("nonexistent-deployment", replicas=2)
    
    assert result["status"] == "error"
    assert "Failed to scale deployment" in result["message"]

if __name__ == "__main__":
    pytest.main([__file__])