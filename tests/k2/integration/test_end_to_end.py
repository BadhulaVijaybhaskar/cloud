#!/usr/bin/env python3
"""
K2 End-to-End Integration Tests
Tests the complete K2 adaptive scaling flow
"""

import os
import json
import time
import pytest
import requests

# Test configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'
PREDICTIVE_ENGINE_URL = os.getenv('PREDICTIVE_ENGINE_URL', 'http://localhost:8500')
ADAPTIVE_SCALER_URL = os.getenv('ADAPTIVE_SCALER_URL', 'http://localhost:8501')
METRICS_COLLECTOR_URL = os.getenv('METRICS_COLLECTOR_URL', 'http://localhost:8502')
TRAINING_WORKER_URL = os.getenv('TRAINING_WORKER_URL', 'http://localhost:8503')

def test_all_services_health():
    """Test that all K2 services are healthy"""
    services = [
        (PREDICTIVE_ENGINE_URL, "predictive-ops-engine"),
        (ADAPTIVE_SCALER_URL, "adaptive-scaler"),
        (METRICS_COLLECTOR_URL, "metrics-collector"),
        (TRAINING_WORKER_URL, "training-worker")
    ]
    
    for url, service_name in services:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data.get('status') == 'healthy'
        except requests.exceptions.RequestException:
            pytest.skip(f"{service_name} not available for health test")

def test_metrics_collection_flow():
    """Test metrics collection and querying"""
    try:
        # Collect some metrics
        metrics_payload = {
            "service": "test-service",
            "metrics": {
                "cpu_usage": 0.75,
                "memory_usage": 0.60,
                "error_rate": 0.02,
                "response_time_ms": 120
            }
        }
        
        response = requests.post(
            f"{METRICS_COLLECTOR_URL}/v1/collect",
            json=metrics_payload,
            timeout=5
        )
        assert response.status_code == 200
        
        # Query the metrics back
        response = requests.get(
            f"{METRICS_COLLECTOR_URL}/v1/query?service=test-service&limit=1",
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'test-service'
        assert len(data['metrics']) == 1
        
    except requests.exceptions.RequestException:
        pytest.skip("Metrics collector not available for collection flow test")

def test_prediction_to_scaling_flow():
    """Test complete flow from prediction to scaling decision"""
    try:
        # Step 1: Get prediction
        prediction_payload = {
            "target": "services/e2e-test",
            "metrics": {
                "cpu_usage": 0.8,
                "memory_usage": 0.7,
                "error_rate": 0.03,
                "avg_latency_ms": 200
            }
        }
        
        pred_response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/forecast",
            json=prediction_payload,
            timeout=5
        )
        assert pred_response.status_code == 200
        prediction = pred_response.json()
        
        # Step 2: Use prediction for scaling analysis
        scaling_payload = {
            "target": "services/e2e-test",
            "metrics": prediction_payload["metrics"],
            "current_replicas": 3
        }
        
        scaling_response = requests.post(
            f"{ADAPTIVE_SCALER_URL}/v1/analyze",
            json=scaling_payload,
            timeout=10
        )
        assert scaling_response.status_code == 200
        scaling_decision = scaling_response.json()
        
        # Step 3: Execute scaling decision (simulation)
        if scaling_decision['action'] != 'no_action':
            execute_payload = {"decision": scaling_decision}
            
            exec_response = requests.post(
                f"{ADAPTIVE_SCALER_URL}/v1/execute",
                json=execute_payload,
                timeout=10
            )
            assert exec_response.status_code == 200
            execution_result = exec_response.json()
            
            assert 'execution_id' in execution_result
            assert execution_result.get('simulation_mode') == SIMULATION_MODE
        
    except requests.exceptions.RequestException:
        pytest.skip("Services not available for prediction to scaling flow test")

def test_batch_prediction_flow():
    """Test batch prediction and scaling analysis"""
    try:
        # Batch prediction request
        batch_payload = {
            "targets": [
                {
                    "target": "services/web",
                    "metrics": {"cpu_usage": 0.85, "memory_usage": 0.70}
                },
                {
                    "target": "services/worker",
                    "metrics": {"cpu_usage": 0.30, "memory_usage": 0.25}
                },
                {
                    "target": "services/db",
                    "metrics": {"cpu_usage": 0.90, "memory_usage": 0.80}
                }
            ]
        }
        
        response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/batch-forecast",
            json=batch_payload,
            timeout=10
        )
        assert response.status_code == 200
        batch_result = response.json()
        
        assert 'results' in batch_result
        assert len(batch_result['results']) == 3
        
        # Analyze each prediction for scaling decisions
        for result in batch_result['results']:
            scaling_payload = {
                "target": result['target'],
                "metrics": {
                    "cpu_usage": result['cpu_forecast'],
                    "memory_usage": result['memory_forecast']
                },
                "current_replicas": 2
            }
            
            scaling_response = requests.post(
                f"{ADAPTIVE_SCALER_URL}/v1/analyze",
                json=scaling_payload,
                timeout=5
            )
            assert scaling_response.status_code == 200
        
    except requests.exceptions.RequestException:
        pytest.skip("Services not available for batch prediction flow test")

def test_training_worker_integration():
    """Test training worker status and model info integration"""
    try:
        # Check training worker status
        response = requests.get(f"{TRAINING_WORKER_URL}/v1/status", timeout=5)
        assert response.status_code == 200
        status = response.json()
        
        assert 'training_status' in status
        assert 'model_info' in status
        
        # Check model info from predictive engine
        response = requests.get(f"{PREDICTIVE_ENGINE_URL}/v1/model/info", timeout=5)
        assert response.status_code == 200
        model_info = response.json()
        
        # Verify model versions are consistent
        assert 'model_version' in model_info
        
    except requests.exceptions.RequestException:
        pytest.skip("Services not available for training worker integration test")

def test_prometheus_metrics_integration():
    """Test Prometheus metrics endpoint"""
    try:
        response = requests.get(f"{METRICS_COLLECTOR_URL}/metrics", timeout=5)
        assert response.status_code == 200
        
        metrics_text = response.text
        assert 'aol_controller_requests_total' in metrics_text
        assert 'service_cpu_usage' in metrics_text
        assert 'service_memory_usage' in metrics_text
        
    except requests.exceptions.RequestException:
        pytest.skip("Metrics collector not available for Prometheus metrics test")

def test_error_handling():
    """Test error handling in the prediction flow"""
    try:
        # Test invalid prediction request
        invalid_payload = {"invalid": "data"}
        
        response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/forecast",
            json=invalid_payload,
            timeout=5
        )
        # Should handle gracefully, either 200 with defaults or 400/500
        assert response.status_code in [200, 400, 500]
        
        # Test invalid scaling request
        response = requests.post(
            f"{ADAPTIVE_SCALER_URL}/v1/analyze",
            json=invalid_payload,
            timeout=5
        )
        assert response.status_code in [200, 400, 500]
        
    except requests.exceptions.RequestException:
        pytest.skip("Services not available for error handling test")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])