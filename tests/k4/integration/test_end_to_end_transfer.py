#!/usr/bin/env python3
"""
K.4 End-to-End Transfer Integration Test
"""
import os
import json
import pytest
import requests

ROOT = os.getenv("ROOT_DIR", ".")
REPORTS = os.path.join(ROOT, "reports/k4")

# Service endpoints
LEARNER_URL = os.getenv('K4_LEARNER_URL', 'http://localhost:8700')
REPOSITORY_URL = os.getenv('K4_REPOSITORY_URL', 'http://localhost:8701')
TRANSFER_URL = os.getenv('K4_TRANSFER_URL', 'http://localhost:8702')
OPTIMIZER_URL = os.getenv('K4_OPTIMIZER_URL', 'http://localhost:8703')

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

def test_simulated_transfer_flow():
    """Simulation-only: validate reports exist and are JSON"""
    assert os.path.exists(REPORTS), "reports/k4 missing"
    files = ["precheck_report.json","deploy_summary.json","transfer_log.json","verification_summary.json"]
    for f in files:
        p = os.path.join(REPORTS, f)
        assert os.path.exists(p), f"{p} missing"
        with open(p) as fh:
            json.load(fh)

def test_full_cognitive_flow():
    """Test complete cognitive optimization flow"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    # Step 1: Extract patterns with cognitive learner
    learn_data = {
        'type': 'scaling_efficiency',
        'data_source': 'operational_metrics'
    }
    
    learn_response = requests.post(f"{LEARNER_URL}/v1/learn", json=learn_data)
    assert learn_response.status_code == 200
    learning = learn_response.json()
    assert learning['simulation'] == True
    
    # Step 2: Store experience in repository
    experience_data = {
        'type': 'scaling_pattern',
        'description': 'Efficient scaling pattern',
        'pattern': learning['pattern']['pattern'],
        'success_rate': learning['pattern']['success_rate'],
        'confidence': learning['pattern']['confidence']
    }
    
    store_response = requests.post(f"{REPOSITORY_URL}/v1/experiences", json=experience_data)
    assert store_response.status_code == 200
    experience = store_response.json()
    assert experience['status'] == 'stored'
    
    # Step 3: Propose knowledge transfer
    transfer_data = {
        'experience_id': experience['experience']['id'],
        'target_workspace': 'test-workspace',
        'type': 'pattern',
        'confidence': 0.85
    }
    
    propose_response = requests.post(f"{TRANSFER_URL}/v1/propose", json=transfer_data)
    assert propose_response.status_code == 200
    proposal = propose_response.json()
    assert proposal['status'] == 'proposed'
    
    # Step 4: Validate optimization
    validate_data = {
        'type': 'scaling',
        'target_service': 'test-service',
        'parameters': {'replicas': 3}
    }
    
    validate_response = requests.post(f"{OPTIMIZER_URL}/v1/validate", json=validate_data)
    assert validate_response.status_code == 200
    validation = validate_response.json()
    assert validation['validation_result'] == 'passed'

def test_knowledge_repository_search():
    """Test experience repository search functionality"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    search_data = {
        'query': 'scaling'
    }
    
    response = requests.post(f"{REPOSITORY_URL}/v1/search", json=search_data)
    assert response.status_code == 200
    
    results = response.json()
    assert 'results' in results
    assert results['simulation'] == True

def test_transfer_approval_workflow():
    """Test transfer approval workflow"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    # List proposals
    response = requests.get(f"{TRANSFER_URL}/v1/proposals")
    assert response.status_code == 200
    
    proposals = response.json()
    if proposals['total'] > 0:
        proposal_id = proposals['proposals'][0]['proposal_id']
        
        # Try to approve (should be simulation only)
        approve_response = requests.post(f"{TRANSFER_URL}/v1/proposals/{proposal_id}/approve")
        assert approve_response.status_code == 200
        
        approval = approve_response.json()
        assert approval['status'] == 'simulation_only'

def test_optimization_metrics():
    """Test optimization metrics collection"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    response = requests.get(f"{OPTIMIZER_URL}/v1/metrics")
    assert response.status_code == 200
    
    metrics = response.json()
    assert 'success_rate' in metrics
    assert 'avg_improvement' in metrics
    assert metrics['simulation'] == True

if __name__ == '__main__':
    pytest.main([__file__, '-v'])