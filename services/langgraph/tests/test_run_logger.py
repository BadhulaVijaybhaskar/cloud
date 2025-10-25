"""
Tests for LangGraph run logger
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the hooks directory to the path
sys.path.append(str(Path(__file__).parent.parent / "hooks"))

from run_logger import log_run, get_runs_by_wpk_id, generate_embedding, upsert_to_milvus

@pytest.fixture
def sample_run():
    """Sample run data for testing"""
    return {
        "wpk_id": "test-workflow-1.0.0",
        "run_id": "run-123",
        "inputs": {"param1": "value1"},
        "outputs": {"text": "workflow completed successfully", "result": "success"},
        "status": "completed",
        "duration_ms": 1500,
        "node_logs": [
            {"node": "start", "message": "Starting workflow"},
            {"node": "process", "message": "Processing data"},
            {"node": "end", "message": "Workflow completed"}
        ]
    }

def test_log_run_success(sample_run):
    """Test successful run logging"""
    run_id = log_run(sample_run)
    assert run_id == sample_run["run_id"]

def test_log_run_missing_required_field():
    """Test run logging with missing required field"""
    invalid_run = {
        "wpk_id": "test-workflow",
        # Missing run_id and status
        "inputs": {}
    }
    
    with pytest.raises(ValueError, match="Missing required field"):
        log_run(invalid_run)

def test_log_run_minimal_data():
    """Test run logging with minimal required data"""
    minimal_run = {
        "wpk_id": "minimal-workflow",
        "run_id": "minimal-123",
        "status": "completed"
    }
    
    run_id = log_run(minimal_run)
    assert run_id == "minimal-123"

def test_get_runs_by_wpk_id(sample_run):
    """Test retrieving runs by workflow package ID"""
    # First log a run
    log_run(sample_run)
    
    # Then retrieve it
    runs = get_runs_by_wpk_id(sample_run["wpk_id"])
    assert len(runs) >= 1
    
    # Check the structure of returned data
    run = runs[0]
    assert len(run) == 4  # run_id, status, duration_ms, created_at
    assert run[0] == sample_run["run_id"]
    assert run[1] == sample_run["status"]

def test_get_runs_by_wpk_id_empty():
    """Test retrieving runs for non-existent workflow"""
    runs = get_runs_by_wpk_id("non-existent-workflow")
    assert runs == []

def test_get_runs_by_wpk_id_pagination():
    """Test pagination in get_runs_by_wpk_id"""
    wpk_id = "pagination-test"
    
    # Log multiple runs
    for i in range(5):
        run_data = {
            "wpk_id": wpk_id,
            "run_id": f"run-{i}",
            "status": "completed"
        }
        log_run(run_data)
    
    # Test pagination
    runs_page1 = get_runs_by_wpk_id(wpk_id, limit=2, offset=0)
    runs_page2 = get_runs_by_wpk_id(wpk_id, limit=2, offset=2)
    
    assert len(runs_page1) == 2
    assert len(runs_page2) == 2
    assert runs_page1[0][0] != runs_page2[0][0]  # Different run_ids

@patch.dict(os.environ, {"OPENAI_KEY": ""})
def test_generate_embedding_no_key():
    """Test embedding generation without OpenAI key"""
    embedding = generate_embedding("test text")
    assert embedding is None

@patch.dict(os.environ, {"OPENAI_KEY": "test-key"})
@patch("run_logger.openai")
def test_generate_embedding_with_key(mock_openai):
    """Test embedding generation with OpenAI key"""
    mock_openai.Embedding.create.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }
    
    embedding = generate_embedding("test text")
    assert embedding == [0.1, 0.2, 0.3]
    mock_openai.Embedding.create.assert_called_once()

@patch.dict(os.environ, {"MILVUS_ENDPOINT": ""})
def test_upsert_to_milvus_no_endpoint():
    """Test Milvus upsert without endpoint"""
    result = upsert_to_milvus("run-123", [0.1, 0.2], {"wpk_id": "test"})
    assert result is False

@patch.dict(os.environ, {"MILVUS_ENDPOINT": "localhost:19530"})
@patch("run_logger.connections")
@patch("run_logger.Collection")
@patch("run_logger.utility")
def test_upsert_to_milvus_success(mock_utility, mock_collection_class, mock_connections):
    """Test successful Milvus upsert"""
    mock_utility.has_collection.return_value = True
    mock_collection = MagicMock()
    mock_collection_class.return_value = mock_collection
    
    result = upsert_to_milvus("run-123", [0.1, 0.2], {"wpk_id": "test", "status": "completed"})
    assert result is True
    mock_collection.insert.assert_called_once()
    mock_collection.flush.assert_called_once()

def test_log_run_with_embedding_integration(sample_run):
    """Test run logging with embedding integration"""
    with patch.dict(os.environ, {"OPENAI_KEY": "test-key"}):
        with patch("run_logger.generate_embedding") as mock_embed:
            with patch("run_logger.upsert_to_milvus") as mock_milvus:
                mock_embed.return_value = [0.1, 0.2, 0.3]
                mock_milvus.return_value = True
                
                run_id = log_run(sample_run)
                
                assert run_id == sample_run["run_id"]
                mock_embed.assert_called_once_with(sample_run["outputs"]["text"])
                mock_milvus.assert_called_once()

def test_database_fallback_logging():
    """Test that sqlite fallback works when postgres unavailable"""
    # This test inherently uses sqlite since POSTGRES_DSN is not set
    test_run = {
        "wpk_id": "fallback-test",
        "run_id": "fallback-123",
        "status": "completed",
        "outputs": {"text": "fallback test"}
    }
    
    run_id = log_run(test_run)
    assert run_id == "fallback-123"
    
    # Verify we can retrieve it
    runs = get_runs_by_wpk_id("fallback-test")
    assert len(runs) >= 1
    assert runs[0][0] == "fallback-123"

if __name__ == "__main__":
    pytest.main([__file__])