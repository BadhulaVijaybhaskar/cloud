#!/usr/bin/env python3
"""
Unit tests for Canary Runner
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from canary_runner import CanaryRunner

def test_canary_runner_initialization():
    """Test canary runner initialization"""
    runner = CanaryRunner(simulation_mode=True)
    assert runner.simulation_mode == True
    assert runner.canary_duration == 300
    assert runner.success_threshold == 0.95

def test_generate_canary_plan():
    """Test canary plan generation"""
    runner = CanaryRunner(simulation_mode=True)
    
    proposal = {
        "id": "test_proposal",
        "scope": "tenant:test",
        "risk_level": "medium",
        "changes": [
            {"path": "scheduler.cpu_limit", "value": 1.5}
        ]
    }
    
    plan = runner.generate_canary_plan(proposal)
    
    assert plan["proposal_id"] == "test_proposal"
    assert plan["scope"] == "tenant:test"
    assert plan["strategy"]["canary_percentage"] == 5  # Medium risk = 5%
    assert len(plan["phases"]) == 4  # prep, deploy, validate, decide
    assert "rollback_plan" in plan

def test_execute_canary_simulation():
    """Test canary execution in simulation mode"""
    runner = CanaryRunner(simulation_mode=True)
    
    canary_plan = {
        "canary_id": "test_canary",
        "proposal_id": "test_proposal",
        "phases": [
            {
                "name": "preparation",
                "duration_seconds": 30,
                "actions": ["snapshot_current_state"]
            },
            {
                "name": "canary_deployment", 
                "duration_seconds": 60,
                "actions": ["deploy_to_canary_subset"]
            }
        ]
    }
    
    result = runner.execute_canary(canary_plan)
    
    assert result["canary_id"] == "test_canary"
    assert result["status"] in ["success", "failed"]
    assert "execution_log" in result
    assert result["simulation_mode"] == True

def test_generate_rollback_plan():
    """Test rollback plan generation"""
    runner = CanaryRunner(simulation_mode=True)
    
    proposal = {
        "changes": [
            {
                "path": "scheduler.cpu_limit",
                "value": 1.5,
                "current_value": 1.0
            }
        ]
    }
    
    rollback_plan = runner.generate_rollback_plan(proposal)
    
    assert "rollback_id" in rollback_plan
    assert len(rollback_plan["changes"]) == 1
    assert rollback_plan["changes"][0]["path"] == "scheduler.cpu_limit"
    assert rollback_plan["changes"][0]["value"] == 1.0  # Reverted value

def test_execute_rollback():
    """Test rollback execution"""
    runner = CanaryRunner(simulation_mode=True)
    
    rollback_plan = {
        "rollback_id": "test_rollback",
        "changes": [
            {"path": "scheduler.cpu_limit", "value": 1.0}
        ]
    }
    
    result = runner.execute_rollback(rollback_plan)
    
    assert result["status"] == "success"
    assert result["rollback_id"] == "test_rollback"
    assert result["simulation_mode"] == True

def test_canary_status_tracking():
    """Test canary status tracking"""
    runner = CanaryRunner(simulation_mode=True)
    
    # Execute a canary
    canary_plan = {
        "canary_id": "status_test",
        "proposal_id": "test_proposal",
        "phases": []
    }
    
    result = runner.execute_canary(canary_plan)
    canary_id = result["canary_id"]
    
    # Check status
    status = runner.get_canary_status(canary_id)
    assert status is not None
    assert status["canary_id"] == canary_id
    
    # List active canaries
    active = runner.list_active_canaries()
    assert len(active) >= 1
    assert any(c["canary_id"] == canary_id for c in active)

def test_abort_canary():
    """Test canary abort functionality"""
    runner = CanaryRunner(simulation_mode=True)
    
    # Execute a canary first
    canary_plan = {
        "canary_id": "abort_test",
        "proposal_id": "test_proposal", 
        "phases": []
    }
    
    result = runner.execute_canary(canary_plan)
    canary_id = result["canary_id"]
    
    # Abort the canary
    abort_result = runner.abort_canary(canary_id, "Test abort")
    
    assert abort_result["status"] == "success"
    assert abort_result["canary_id"] == canary_id
    assert abort_result["abort_reason"] == "Test abort"

if __name__ == "__main__":
    pytest.main([__file__])