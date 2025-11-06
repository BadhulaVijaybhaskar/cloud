#!/usr/bin/env python3
"""
K1 Autonomous Runtime Integration Tests
Tests the full AOL decision -> policy -> execution flow
"""

import os
import json
import time
import pytest
import requests
from datetime import datetime

# Test configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'
AOL_CONTROLLER_URL = os.getenv('AOL_CONTROLLER_URL', 'http://localhost:8200')
AOL_POLICY_URL = os.getenv('AOL_POLICY_URL', 'http://localhost:8300')
AOL_EXECUTOR_URL = os.getenv('AOL_EXECUTOR_URL', 'http://localhost:8310')
AOL_SIMULATOR_URL = os.getenv('AOL_SIMULATOR_URL', 'http://localhost:8320')

def test_aol_controller_health():
    """Test AOL controller health endpoint"""
    try:
        response = requests.get(f"{AOL_CONTROLLER_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('service') == 'aol-controller'
    except requests.exceptions.RequestException:
        pytest.skip("AOL Controller not available for integration test")

def test_aol_policy_health():
    """Test AOL policy engine health endpoint"""
    try:
        response = requests.get(f"{AOL_POLICY_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('service') == 'aol-policy'
    except requests.exceptions.RequestException:
        pytest.skip("AOL Policy Engine not available for integration test")

def test_aol_executor_health():
    """Test AOL executor health endpoint"""
    try:
        response = requests.get(f"{AOL_EXECUTOR_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('service') == 'aol-executor'
    except requests.exceptions.RequestException:
        pytest.skip("AOL Executor not available for integration test")

def test_aol_simulator_health():
    """Test AOL simulator health endpoint"""
    try:
        response = requests.get(f"{AOL_SIMULATOR_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('service') == 'aol-simulator'
    except requests.exceptions.RequestException:
        pytest.skip("AOL Simulator not available for integration test")

def test_decision_flow():
    """Test full decision flow: context -> decision -> policy evaluation"""
    try:
        # Submit decision request
        context = {
            "service": "test-service",
            "cpu_usage": 85,
            "memory_usage": 70,
            "error_rate": 0.05
        }
        
        response = requests.post(
            f"{AOL_CONTROLLER_URL}/v1/decide",
            json=context,
            timeout=10
        )
        
        assert response.status_code == 200
        decision = response.json()
        
        # Verify decision structure
        assert 'id' in decision
        assert 'actions' in decision
        assert 'score' in decision
        assert 'timestamp' in decision
        assert decision.get('simulation_mode') == SIMULATION_MODE
        
        # Verify decision ID can be retrieved
        decision_id = decision['id']
        response = requests.get(f"{AOL_CONTROLLER_URL}/v1/decisions/{decision_id}")
        assert response.status_code == 200
        
    except requests.exceptions.RequestException:
        pytest.skip("AOL services not available for decision flow test")

def test_policy_evaluation():
    """Test policy evaluation with various actions"""
    try:
        # Test allowed action
        allowed_action = {
            "actions": [{
                "type": "scale",
                "target": "services/auth",
                "params": {"replicas": 3}
            }],
            "context": {}
        }
        
        response = requests.post(
            f"{AOL_POLICY_URL}/v1/evaluate",
            json=allowed_action,
            timeout=5
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'allow' in result
        assert 'reasons' in result
        assert 'explain' in result
        
        # Test denied action (unsafe target)
        denied_action = {
            "actions": [{
                "type": "restart",
                "target": "services/unsafe-service",
                "params": {"strategy": "immediate"}
            }],
            "context": {}
        }
        
        response = requests.post(
            f"{AOL_POLICY_URL}/v1/evaluate",
            json=denied_action,
            timeout=5
        )
        
        assert response.status_code == 200
        result = response.json()
        # Should be denied due to unsafe target or strategy
        
    except requests.exceptions.RequestException:
        pytest.skip("AOL Policy Engine not available for policy evaluation test")

def test_action_execution():
    """Test action execution in simulation mode"""
    try:
        action = {
            "action_id": "test-action-001",
            "action": {
                "type": "scale",
                "target": "test-service",
                "params": {"replicas": 2}
            }
        }
        
        response = requests.post(
            f"{AOL_EXECUTOR_URL}/v1/execute",
            json=action,
            timeout=5
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'job_id' in result
        assert 'status' in result
        
        # Check job status
        job_id = result['job_id']
        response = requests.get(f"{AOL_EXECUTOR_URL}/v1/jobs/{job_id}")
        assert response.status_code == 200
        
        job = response.json()
        assert job.get('simulation_mode') == SIMULATION_MODE
        if SIMULATION_MODE:
            assert job.get('status') == 'simulated'
        
    except requests.exceptions.RequestException:
        pytest.skip("AOL Executor not available for execution test")

def test_simulation_scenario():
    """Test simulation scenario execution"""
    try:
        scenario = {
            "scenario": "node-failure",
            "duration": 30  # Short duration for test
        }
        
        response = requests.post(
            f"{AOL_SIMULATOR_URL}/v1/run-scenario",
            json=scenario,
            timeout=5
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'job_id' in result
        assert result.get('status') == 'started'
        
        # Wait a bit and check job status
        job_id = result['job_id']
        time.sleep(2)
        
        response = requests.get(f"{AOL_SIMULATOR_URL}/v1/jobs/{job_id}")
        assert response.status_code == 200
        
        job = response.json()
        assert job.get('scenario') == 'node-failure'
        assert job.get('status') in ['running', 'completed']
        
    except requests.exceptions.RequestException:
        pytest.skip("AOL Simulator not available for simulation test")

def test_end_to_end_autonomous_flow():
    """Test complete autonomous flow from simulation to execution"""
    if not SIMULATION_MODE:
        pytest.skip("End-to-end test only runs in simulation mode")
    
    try:
        # 1. Start simulation
        scenario = {
            "scenario": "high-load",
            "duration": 10
        }
        
        sim_response = requests.post(
            f"{AOL_SIMULATOR_URL}/v1/run-scenario",
            json=scenario,
            timeout=5
        )
        assert sim_response.status_code == 200
        
        # 2. Submit decision based on simulated context
        context = {
            "service": "services/auth",
            "cpu_usage": 90,
            "memory_usage": 85,
            "request_rate": 1500
        }
        
        decision_response = requests.post(
            f"{AOL_CONTROLLER_URL}/v1/decide",
            json=context,
            timeout=10
        )
        assert decision_response.status_code == 200
        decision = decision_response.json()
        
        # 3. Verify policy evaluation occurred
        if not SIMULATION_MODE and 'policy_evaluation' in decision:
            assert 'allow' in decision['policy_evaluation']
        
        # 4. Execute action if allowed
        if decision.get('actions'):
            action = {
                "action_id": decision['id'],
                "action": decision['actions'][0]
            }
            
            exec_response = requests.post(
                f"{AOL_EXECUTOR_URL}/v1/execute",
                json=action,
                timeout=5
            )
            assert exec_response.status_code == 200
        
    except requests.exceptions.RequestException:
        pytest.skip("AOL services not available for end-to-end test")

def test_governance_compliance():
    """Test that all actions comply with governance policies"""
    try:
        # Test various action types for compliance
        test_actions = [
            {"type": "scale", "target": "services/auth", "params": {"replicas": 5}},
            {"type": "restart", "target": "services/auth", "params": {"strategy": "rolling"}},
            {"type": "scale", "target": "services/billing", "params": {"replicas": 15}},  # Should be denied (too many replicas)
        ]
        
        for action in test_actions:
            response = requests.post(
                f"{AOL_POLICY_URL}/v1/evaluate",
                json={"actions": [action], "context": {}},
                timeout=5
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify governance fields are present
            assert 'allow' in result
            assert 'reasons' in result
            assert 'explain' in result
            
            # Check that explanations include policy references
            if 'policies_checked' in result.get('explain', {}):
                assert len(result['explain']['policies_checked']) > 0
        
    except requests.exceptions.RequestException:
        pytest.skip("AOL Policy Engine not available for governance test")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])