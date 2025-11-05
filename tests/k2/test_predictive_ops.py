#!/usr/bin/env python3
"""
K2 Predictive Ops Tests
Tests for predictive ops engine functionality
"""

import os
import json
import pytest
import requests
from datetime import datetime

# Test configuration
PREDICTIVE_ENGINE_URL = os.getenv('PREDICTIVE_ENGINE_URL', 'http://localhost:8500')

def test_predictive_engine_health():
    """Test predictive ops engine health endpoint"""
    try:
        response = requests.get(f"{PREDICTIVE_ENGINE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('service') == 'predictive-ops-engine'
    except requests.exceptions.RequestException:
        pytest.skip("Predictive ops engine not available for test")

def test_forecast_endpoint():
    """Test forecast generation"""
    try:
        payload = {
            "target": "services/test",
            "metrics": {
                "cpu_usage": 0.6,
                "memory_usage": 0.5,
                "error_rate": 0.02,
                "avg_latency_ms": 150
            }
        }
        
        response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/forecast",
            json=payload,
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'id' in data
        assert 'target' in data
        assert 'timestamp' in data
        assert 'predictions' in data
        
        predictions = data['predictions']
        assert 'load' in predictions
        assert 'failure' in predictions
        
        # Verify load predictions
        load_pred = predictions['load']
        assert 'cpu_forecast' in load_pred
        assert 'memory_forecast' in load_pred
        assert 'confidence' in load_pred
        
        # Verify failure predictions
        failure_pred = predictions['failure']
        assert 'failure_probability' in failure_pred
        
    except requests.exceptions.RequestException:
        pytest.skip("Predictive ops engine not available for forecast test")

def test_batch_forecast():
    """Test batch forecast functionality"""
    try:
        payload = {
            "targets": [
                {
                    "target": "services/web",
                    "metrics": {"cpu_usage": 0.7, "memory_usage": 0.6}
                },
                {
                    "target": "services/worker", 
                    "metrics": {"cpu_usage": 0.4, "memory_usage": 0.3}
                }
            ]
        }
        
        response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/batch-forecast",
            json=payload,
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'batch_id' in data
        assert 'results' in data
        assert len(data['results']) == 2
        
        for result in data['results']:
            assert 'target' in result
            assert 'cpu_forecast' in result
            assert 'failure_prob' in result
            
    except requests.exceptions.RequestException:
        pytest.skip("Predictive ops engine not available for batch forecast test")

def test_model_info():
    """Test model information endpoint"""
    try:
        response = requests.get(f"{PREDICTIVE_ENGINE_URL}/v1/model/info", timeout=5)
        assert response.status_code == 200
        data = response.json()
        
        assert 'model_version' in data
        assert 'model_type' in data
        assert 'features' in data
        assert 'accuracy_metrics' in data
        
    except requests.exceptions.RequestException:
        pytest.skip("Predictive ops engine not available for model info test")

def test_forecast_validation():
    """Test forecast output validation"""
    try:
        payload = {
            "target": "services/validation-test",
            "metrics": {
                "cpu_usage": 0.8,
                "memory_usage": 0.7,
                "error_rate": 0.05
            }
        }
        
        response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/forecast",
            json=payload,
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate forecast ranges
        load_pred = data['predictions']['load']
        assert 0.0 <= load_pred['cpu_forecast'] <= 1.0
        assert 0.0 <= load_pred['memory_forecast'] <= 1.0
        assert 0.0 <= load_pred['confidence'] <= 1.0
        
        failure_pred = data['predictions']['failure']
        assert 0.0 <= failure_pred['failure_probability'] <= 1.0
        
    except requests.exceptions.RequestException:
        pytest.skip("Predictive ops engine not available for validation test")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])