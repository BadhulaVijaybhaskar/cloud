#!/usr/bin/env python3
"""
K.3 Full Flow Integration Test
End-to-end incident → healing validation
"""
import pytest
import requests
import time
import os

# Service endpoints
DETECTOR_URL = os.getenv('K3_DETECTOR_URL', 'http://localhost:8600')
PLANNER_URL = os.getenv('K3_PLANNER_URL', 'http://localhost:8601')
EXECUTOR_URL = os.getenv('K3_EXECUTOR_URL', 'http://localhost:8602')
INDEXER_URL = os.getenv('K3_INDEXER_URL', 'http://localhost:8603')

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

def test_full_healing_flow():
    """Test complete incident detection → healing flow"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    # Step 1: Detect incident
    incident_data = {
        'type': 'service_crash',
        'service': 'test-service',
        'severity': 'high'
    }
    
    detect_response = requests.post(f"{DETECTOR_URL}/v1/detect", json=incident_data)
    assert detect_response.status_code == 200
    incident = detect_response.json()
    incident_id = incident['id']
    
    # Step 2: Create healing plan
    plan_data = {
        'incident_id': incident_id,
        'type': incident['type'],
        'severity': incident['severity']
    }
    
    plan_response = requests.post(f"{PLANNER_URL}/v1/plan", json=plan_data)
    assert plan_response.status_code == 200
    plan = plan_response.json()
    
    assert plan['incident_id'] == incident_id
    assert len(plan['strategies']) > 0
    recommended_action = plan['recommended_action']
    
    # Step 3: Execute healing action
    execute_data = {
        'action': recommended_action['action'],
        'target': incident['service'],
        'incident_id': incident_id
    }
    
    execute_response = requests.post(f"{EXECUTOR_URL}/v1/execute", json=execute_data)
    assert execute_response.status_code == 200
    execution = execute_response.json()
    
    assert execution['success'] == True
    assert execution['action'] == recommended_action['action']
    action_id = execution['action_id']
    
    # Step 4: Index resolution pattern
    index_data = {
        'incident_id': incident_id,
        'incident_type': incident['type'],
        'action_taken': recommended_action['action'],
        'success': execution['success'],
        'recovery_time': execution['duration_seconds']
    }
    
    index_response = requests.post(f"{INDEXER_URL}/v1/index", json=index_data)
    assert index_response.status_code == 200
    index_result = index_response.json()
    
    assert index_result['status'] == 'indexed'
    assert index_result['pattern']['incident_id'] == incident_id
    
    # Step 5: Verify knowledge base updated
    knowledge_response = requests.get(f"{INDEXER_URL}/v1/knowledge?type={incident['type']}")
    assert knowledge_response.status_code == 200
    knowledge = knowledge_response.json()
    
    assert len(knowledge['patterns']) > 0

def test_healing_with_rollback():
    """Test healing flow with rollback scenario"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    # Simulate failed healing action
    execute_data = {
        'action': 'restart_service',
        'target': 'failing-service'
    }
    
    execute_response = requests.post(f"{EXECUTOR_URL}/v1/execute", json=execute_data)
    assert execute_response.status_code == 200
    execution = execute_response.json()
    action_id = execution['action_id']
    
    # Test rollback
    rollback_response = requests.post(f"{EXECUTOR_URL}/v1/actions/{action_id}/rollback")
    assert rollback_response.status_code == 200
    rollback = rollback_response.json()
    
    assert rollback['rollback_status'] == 'completed'

def test_knowledge_recommendation():
    """Test knowledge-based action recommendation"""
    if not SIMULATION_MODE:
        pytest.skip("Live mode not implemented")
    
    recommend_data = {
        'incident_type': 'service_crash'
    }
    
    response = requests.post(f"{INDEXER_URL}/v1/recommend", json=recommend_data)
    assert response.status_code == 200
    
    recommendation = response.json()
    assert 'recommended_action' in recommendation
    assert 'confidence' in recommendation
    assert recommendation['confidence'] > 0.5

if __name__ == '__main__':
    pytest.main([__file__, '-v'])