import pytest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../services/l6-orchestrator/src'))

def test_orchestrator_health():
    """Test orchestrator health endpoint"""
    from main import app
    client = app.test_client()
    
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['component'] == 'l6-orchestrator'

def test_observe_endpoint():
    """Test observation endpoint"""
    os.environ['SIMULATION_MODE'] = 'true'
    from main import app
    client = app.test_client()
    
    response = client.post('/v1/observe', json={'metrics': [{'cpu': 50}]})
    assert response.status_code == 202
    data = response.get_json()
    assert data['simulated'] is True

def test_propose_endpoint():
    """Test proposal endpoint"""
    os.environ['SIMULATION_MODE'] = 'true'
    from main import app
    client = app.test_client()
    
    response = client.post('/v1/propose', json={'action': 'scale'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['simulated'] is True
    assert 'proposal_id' in data