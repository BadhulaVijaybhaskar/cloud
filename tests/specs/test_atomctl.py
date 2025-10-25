import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import sys

# Add the CLI directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "cli" / "atomctl"))

from main import atomctl, AtomCLI

@pytest.fixture
def runner():
    """Click test runner"""
    return CliRunner()

@pytest.fixture
def sample_wpk():
    """Sample WPK content"""
    return {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "Test workflow",
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
def temp_wpk_file(sample_wpk):
    """Create temporary WPK file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.wpk.yaml', delete=False) as f:
        yaml.dump(sample_wpk, f, default_flow_style=False)
        return f.name

def test_cli_initialization():
    """Test CLI initialization"""
    cli = AtomCLI()
    assert 'registry_url' in cli.config
    assert 'runtime_url' in cli.config

def test_validate_command_success(runner, temp_wpk_file):
    """Test successful WPK validation"""
    result = runner.invoke(atomctl, ['validate', temp_wpk_file])
    
    assert result.exit_code == 0
    assert "✅ WPK validation passed" in result.output
    assert "Name: test-workflow" in result.output
    assert "Version: 1.0.0" in result.output

def test_validate_command_missing_file(runner):
    """Test validation with missing file"""
    result = runner.invoke(atomctl, ['validate', 'nonexistent.wpk.yaml'])
    
    assert result.exit_code != 0

def test_validate_command_invalid_wpk(runner):
    """Test validation with invalid WPK"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.wpk.yaml', delete=False) as f:
        yaml.dump({"invalid": "structure"}, f)
        invalid_file = f.name
    
    result = runner.invoke(atomctl, ['validate', invalid_file])
    
    assert result.exit_code == 0
    assert "❌ Validation failed" in result.output
    assert "Missing required field" in result.output

def test_pack_command_success(runner, temp_wpk_file):
    """Test successful WPK packing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test-output.tar.gz"
        
        result = runner.invoke(atomctl, ['pack', temp_wpk_file, '--output', str(output_path)])
        
        assert result.exit_code == 0
        assert "📦 Packed WPK" in result.output
        assert output_path.exists()

def test_pack_command_with_sign(runner, temp_wpk_file):
    """Test WPK packing with signing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test-signed.tar.gz"
        
        result = runner.invoke(atomctl, ['pack', temp_wpk_file, '--output', str(output_path), '--sign'])
        
        assert result.exit_code == 0
        assert "✅ Signed and packed" in result.output

@patch('requests.post')
def test_push_command_success(mock_post, runner, temp_wpk_file):
    """Test successful WPK push"""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "workflow_id": "test-workflow-1.0.0",
        "status": "registered"
    }
    mock_post.return_value = mock_response
    
    result = runner.invoke(atomctl, ['push', temp_wpk_file])
    
    assert result.exit_code == 0
    assert "✅ WPK pushed successfully" in result.output
    assert "Workflow ID: test-workflow-1.0.0" in result.output

@patch('requests.post')
def test_push_command_unsigned_wpk(mock_post, runner):
    """Test push with unsigned WPK"""
    # Create unsigned WPK
    unsigned_wpk = {
        "apiVersion": "v1",
        "kind": "WorkflowPackage",
        "metadata": {
            "name": "unsigned-workflow",
            "version": "1.0.0",
            "description": "Unsigned workflow",
            "author": "Test Author"
            # No signature
        },
        "spec": {
            "runtime": {"type": "k8s"},
            "safety": {"mode": "manual"},
            "handlers": [{"name": "test", "type": "k8s", "config": {}}]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.wpk.yaml', delete=False) as f:
        yaml.dump(unsigned_wpk, f)
        unsigned_file = f.name
    
    result = runner.invoke(atomctl, ['push', unsigned_file])
    
    assert result.exit_code == 0
    assert "❌ WPK must be signed before pushing" in result.output

@patch('requests.post')
def test_push_command_failure(mock_post, runner, temp_wpk_file):
    """Test push failure"""
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Invalid WPK"}
    mock_response.headers = {"content-type": "application/json"}
    mock_post.return_value = mock_response
    
    result = runner.invoke(atomctl, ['push', temp_wpk_file])
    
    assert result.exit_code == 0
    assert "❌ Push failed: 400" in result.output

@patch('requests.get')
@patch('requests.post')
def test_run_command_success(mock_post, mock_get, runner):
    """Test successful workflow run"""
    # Mock workflow fetch
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "wpk_content": {
            "metadata": {"name": "test-workflow"},
            "spec": {"handlers": []}
        }
    }
    mock_get.return_value = mock_get_response
    
    # Mock execution start
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {
        "execution_id": "exec-123",
        "status": "started"
    }
    mock_post.return_value = mock_post_response
    
    result = runner.invoke(atomctl, ['run', 'test-workflow-1.0.0'])
    
    assert result.exit_code == 0
    assert "✅ Execution started" in result.output
    assert "Execution ID: exec-123" in result.output

@patch('requests.get')
def test_run_command_workflow_not_found(mock_get, runner):
    """Test run with non-existent workflow"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = runner.invoke(atomctl, ['run', 'nonexistent-workflow'])
    
    assert result.exit_code == 0
    assert "❌ Failed to fetch workflow: 404" in result.output

def test_run_command_invalid_parameters(runner):
    """Test run with invalid parameters JSON"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"wpk_content": {}}
        mock_get.return_value = mock_response
        
        result = runner.invoke(atomctl, ['run', 'test-workflow', '--parameters', 'invalid-json'])
        
        assert result.exit_code == 0
        assert "❌ Invalid parameters JSON" in result.output

@patch('requests.get')
def test_list_command_success(mock_get, runner):
    """Test successful workflow listing"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "workflows": [
            {
                "name": "test-workflow",
                "version": "1.0.0",
                "id": "test-workflow-1.0.0",
                "author": "Test Author",
                "runtime_type": "k8s",
                "safety_mode": "manual",
                "created": "2024-01-15T10:00:00Z",
                "tags": ["test", "example"]
            }
        ]
    }
    mock_get.return_value = mock_response
    
    result = runner.invoke(atomctl, ['list'])
    
    assert result.exit_code == 0
    assert "📋 Found 1 workflows" in result.output
    assert "🔧 test-workflow v1.0.0" in result.output
    assert "Author: Test Author" in result.output

@patch('requests.get')
def test_list_command_empty(mock_get, runner):
    """Test listing with no workflows"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"workflows": []}
    mock_get.return_value = mock_response
    
    result = runner.invoke(atomctl, ['list'])
    
    assert result.exit_code == 0
    assert "📭 No workflows found in registry" in result.output

@patch('requests.get')
def test_status_command_success(mock_get, runner):
    """Test successful status check"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "workflow_id": "test-workflow-1.0.0",
        "status": "running",
        "started_at": "2024-01-15T10:00:00Z",
        "current_step": "test-handler",
        "steps_completed": 1,
        "total_steps": 3,
        "logs": ["Handler started", "Processing..."]
    }
    mock_get.return_value = mock_response
    
    result = runner.invoke(atomctl, ['status', 'exec-123'])
    
    assert result.exit_code == 0
    assert "📊 Execution Status: exec-123" in result.output
    assert "Status: running" in result.output
    assert "Progress: 1/3" in result.output

@patch('requests.get')
def test_status_command_not_found(mock_get, runner):
    """Test status check for non-existent execution"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = runner.invoke(atomctl, ['status', 'nonexistent-exec'])
    
    assert result.exit_code == 0
    assert "❌ Failed to get status: 404" in result.output

def test_config_command(runner):
    """Test configuration command"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        
        with patch('main.CONFIG_FILE', config_file):
            result = runner.invoke(atomctl, [
                'config',
                '--registry-url', 'http://test-registry:8000',
                '--runtime-url', 'http://test-runtime:4000',
                '--auth-token', 'test-token-123'
            ])
            
            assert result.exit_code == 0
            assert "✅ Registry URL set to: http://test-registry:8000" in result.output
            assert "✅ Runtime URL set to: http://test-runtime:4000" in result.output
            assert "✅ Auth token configured" in result.output

def test_config_display(runner):
    """Test configuration display"""
    result = runner.invoke(atomctl, ['config'])
    
    assert result.exit_code == 0
    assert "📋 Current Configuration:" in result.output
    assert "Registry URL:" in result.output
    assert "Runtime URL:" in result.output

def test_help_command(runner):
    """Test help command"""
    result = runner.invoke(atomctl, ['--help'])
    
    assert result.exit_code == 0
    assert "ATOM Cloud CLI - Manage workflow packages" in result.output
    assert "pack" in result.output
    assert "validate" in result.output
    assert "push" in result.output
    assert "run" in result.output

def test_version_command(runner):
    """Test version command"""
    result = runner.invoke(atomctl, ['--version'])
    
    assert result.exit_code == 0
    assert "1.0.0" in result.output

if __name__ == "__main__":
    pytest.main([__file__])