import pytest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../services/l5-orchestrator/src'))

def test_orchestrator_health():
    """Test orchestrator health endpoint"""
    from main import app
    client = app.test_client()
    
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['component'] == 'l5-orchestrator'

def test_rollout_simulation():
    """Test rollout in simulation mode"""
    os.environ['SIMULATION_MODE'] = 'true'
    from main import app
    client = app.test_client()
    
    response = client.post('/v1/rollout', json={'plan': 'canary'})
    assert response.status_code == 202
    data = response.get_json()
    assert data['simulated'] is True