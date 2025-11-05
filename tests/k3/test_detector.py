#!/usr/bin/env python3
"""
K.3 Incident Detector Tests
"""
import pytest
import requests
import json
import os

BASE_URL = os.getenv('K3_DETECTOR_URL', 'http://localhost:8600')
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

def test_detector_health():
    """Test detector service health"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['simulation_mode'] == SIMULATION_MODE

def test_detect_service_crash():
    """Test service crash detection"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    incident_data = {
        'type': 'service_crash',
        'service': 'test-service',
        'severity': 'high'
    }
    
    response = requests.post(f"{BASE_URL}/v1/detect", json=incident_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data['type'] == 'service_crash'
    assert data['severity'] == 'high'
    assert data['service'] == 'test-service'
    assert 'id' in data
    assert data['simulation'] == True

def test_detect_latency_spike():
    """Test latency spike detection"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    incident_data = {
        'type': 'latency_spike',
        'service': 'api-service'
    }
    
    response = requests.post(f"{BASE_URL}/v1/detect", json=incident_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data['type'] == 'latency_spike'
    assert data['correlation_score'] > 0.9

def test_list_incidents():
    """Test incident listing"""
    response = requests.get(f"{BASE_URL}/v1/incidents")
    assert response.status_code == 200
    
    data = response.json()
    assert 'incidents' in data
    if SIMULATION_MODE:
        assert data['simulation'] == True

if __name__ == '__main__':
    pytest.main([__file__, '-v'])