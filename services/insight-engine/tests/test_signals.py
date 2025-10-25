"""
Tests for Insight Engine signals
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the service directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from server import app, query_prometheus, compute_z_score, compute_ewma_score, store_signal

client = TestClient(app)

@pytest.fixture
def mock_prometheus_response():
    """Mock Prometheus API response"""
    return {
        "status": "success",
        "data": {
            "result": [
                {
                    "metric": {"__name__": "cpu_usage"},
                    "values": [
                        [1640995200, "0.5"],
                        [1640995260, "0.6"],
                        [1640995320, "0.7"],
                        [1640995380, "0.8"],
                        [1640995440, "2.5"]  # Anomaly
                    ]
                }
            ]
        }
    }

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "prometheus_url" in data

@patch('server.requests.get')
def test_query_prometheus_success(mock_get, mock_prometheus_response):
    """Test successful Prometheus query"""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_prometheus_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    results = query_prometheus("cpu_usage", 60)
    
    assert len(results) == 1
    assert results[0]["metric"] == "cpu_usage"
    assert len(results[0]["values"]) == 5
    assert results[0]["values"][-1][1] == 2.5  # Last value

@patch('server.requests.get')
def test_query_prometheus_failure(mock_get):
    """Test Prometheus query failure fallback"""
    mock_get.side_effect = Exception("Connection failed")
    
    results = query_prometheus("cpu_usage", 60)
    
    # Should return mock data
    assert len(results) == 1
    assert results[0]["metric"] == "cpu_usage"

def test_compute_z_score():
    """Test z-score calculation"""
    values = [1.0, 1.1, 0.9, 1.2, 0.8]
    current_value = 3.0  # Clear outlier
    
    z_score = compute_z_score(values, current_value)
    assert z_score > 2.0  # Should be high anomaly score

def test_compute_z_score_no_variance():
    """Test z-score with no variance"""
    values = [1.0, 1.0, 1.0, 1.0]
    current_value = 1.0
    
    z_score = compute_z_score(values, current_value)
    assert z_score == 0.0

def test_compute_z_score_insufficient_data():
    """Test z-score with insufficient data"""
    values = [1.0]
    current_value = 2.0
    
    z_score = compute_z_score(values, current_value)
    assert z_score == 0.0

def test_compute_ewma_score():
    """Test EWMA score calculation"""
    values = [1.0, 1.1, 0.9, 1.2, 3.0]  # Last value is anomaly
    
    ewma_score = compute_ewma_score(values)
    assert ewma_score > 0.0

def test_compute_ewma_score_insufficient_data():
    """Test EWMA with insufficient data"""
    values = [1.0]
    
    ewma_score = compute_ewma_score(values)
    assert ewma_score == 0.0

def test_store_signal():
    """Test signal storage"""
    signal_id = store_signal("test_metric", 1.5, 2.3, "Test anomaly")
    
    assert signal_id is not None
    assert len(signal_id) > 0

@patch('server.query_prometheus')
def test_probe_endpoint_anomaly_detected(mock_query):
    """Test probe endpoint with anomaly detection"""
    # Mock Prometheus data with anomaly
    mock_query.return_value = [{
        "metric": "cpu_usage",
        "values": [(1640995200, 0.5), (1640995260, 0.6), (1640995320, 5.0)]  # Last value is anomaly
    }]
    
    response = client.post("/probe", json={
        "query": "cpu_usage",
        "threshold": 2.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "signal_id" in data
    assert data["score"] >= 2.0
    assert data["metric"] == "cpu_usage"
    assert "anomaly detected" in data["hint"].lower()

@patch('server.query_prometheus')
def test_probe_endpoint_no_anomaly(mock_query):
    """Test probe endpoint with no anomaly"""
    # Mock normal Prometheus data
    mock_query.return_value = [{
        "metric": "cpu_usage",
        "values": [(1640995200, 0.5), (1640995260, 0.6), (1640995320, 0.7)]
    }]
    
    response = client.post("/probe", json={
        "query": "cpu_usage",
        "threshold": 2.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["score"] < 2.0
    assert "no anomaly" in data["hint"].lower()

@patch('server.query_prometheus')
def test_probe_endpoint_no_data(mock_query):
    """Test probe endpoint with no Prometheus data"""
    mock_query.return_value = []
    
    response = client.post("/probe", json={
        "query": "nonexistent_metric",
        "threshold": 2.0
    })
    
    assert response.status_code == 400
    assert "No data returned" in response.json()["detail"]

def test_get_signals_endpoint():
    """Test get signals endpoint"""
    # First store a signal
    store_signal("test_metric", 1.5, 2.3, "Test signal")
    
    response = client.get("/signals")
    assert response.status_code == 200
    data = response.json()
    assert "signals" in data
    assert "total" in data
    assert isinstance(data["signals"], list)

def test_get_signals_with_metric_filter():
    """Test get signals with metric filter"""
    # Store signals for different metrics
    store_signal("metric_a", 1.0, 2.0, "Signal A")
    store_signal("metric_b", 2.0, 3.0, "Signal B")
    
    response = client.get("/signals?metric=metric_a")
    assert response.status_code == 200
    data = response.json()
    
    # Should only return signals for metric_a
    for signal in data["signals"]:
        assert signal["metric"] == "metric_a"

def test_get_signals_with_limit():
    """Test get signals with limit"""
    # Store multiple signals
    for i in range(10):
        store_signal(f"metric_{i}", float(i), float(i), f"Signal {i}")
    
    response = client.get("/signals?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["signals"]) <= 5

def test_probe_request_validation():
    """Test probe request validation"""
    # Missing query
    response = client.post("/probe", json={
        "threshold": 2.0
    })
    assert response.status_code == 422  # Validation error
    
    # Invalid threshold type
    response = client.post("/probe", json={
        "query": "cpu_usage",
        "threshold": "invalid"
    })
    assert response.status_code == 422  # Validation error

def test_probe_with_custom_parameters():
    """Test probe with custom parameters"""
    with patch('server.query_prometheus') as mock_query:
        mock_query.return_value = [{
            "metric": "memory_usage",
            "values": [(1640995200, 0.8), (1640995260, 0.9), (1640995320, 0.85)]
        }]
        
        response = client.post("/probe", json={
            "query": "memory_usage",
            "threshold": 1.5,
            "lookback_minutes": 120
        })
        
        assert response.status_code == 200
        # Verify custom parameters were used
        mock_query.assert_called_once_with("memory_usage", 120)

if __name__ == "__main__":
    pytest.main([__file__])