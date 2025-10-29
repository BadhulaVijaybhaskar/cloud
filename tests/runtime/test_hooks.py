import pytest
import sys
import os

# Add services to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'neural-fabric-scheduler'))

from runtime_hooks import check_frameworks, get_runtime, load_model, validate_runtime_performance

def test_check_frameworks():
    """Test framework availability check"""
    frameworks = check_frameworks()
    assert isinstance(frameworks, dict)
    assert "pytorch" in frameworks
    assert "tensorflow" in frameworks
    assert "onnx" in frameworks

def test_get_runtime():
    """Test runtime initialization"""
    runtime = get_runtime("pytorch")
    assert runtime is not None
    assert runtime.framework == "pytorch"

def test_load_model():
    """Test model loading"""
    result = load_model("pytorch", "test_model")
    assert "model" in result
    assert "framework" in result
    assert "load_time_ms" in result
    assert result["framework"] == "pytorch"

def test_validate_runtime_performance():
    """Test P6 performance validation"""
    results = validate_runtime_performance()
    assert isinstance(results, dict)
    
    for framework, result in results.items():
        assert "load_time_ms" in result
        assert "p6_compliant" in result
        assert "status" in result
        # In simulation mode, should be fast
        assert result["load_time_ms"] < 800  # P6 requirement