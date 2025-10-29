#!/usr/bin/env python3
"""Tests for Confidence Scorer"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "confidence-scorer"

def test_score_proposal():
    """Test scoring a proposal"""
    score_data = {
        "proposal_id": "prop-test-001",
        "manifest": {
            "action": "scale_up",
            "target": "compute_instances",
            "impact_level": "medium",
            "rollback_plan": True,
            "parameters": {"target_count": 3, "instance_type": "t3.medium"}
        }
    }
    
    response = client.post("/score", json=score_data)
    assert response.status_code == 200
    data = response.json()
    
    assert "score" in data
    assert "confidence" in data["score"]
    assert "risk" in data["score"]
    assert "cost_estimate" in data["score"]
    assert "explanation" in data["score"]
    assert 0.0 <= data["score"]["confidence"] <= 1.0
    assert 0.0 <= data["score"]["risk"] <= 1.0

def test_high_risk_action():
    """Test scoring a high-risk action"""
    score_data = {
        "proposal_id": "prop-test-002",
        "manifest": {
            "action": "delete",
            "target": "database",
            "impact_level": "high",
            "rollback_plan": False
        }
    }
    
    response = client.post("/score", json=score_data)
    assert response.status_code == 200
    data = response.json()
    
    # High-risk actions should have higher risk scores
    assert data["score"]["risk"] > 0.5
    assert "risk" in data["score"]["explanation"].lower()

def test_cost_estimation():
    """Test cost estimation for different actions"""
    # Scale up should have positive cost
    scale_up_data = {
        "proposal_id": "prop-cost-001",
        "manifest": {
            "action": "scale_up",
            "parameters": {"target_count": 4, "instance_type": "c5.large"}
        }
    }
    
    response = client.post("/score", json=scale_up_data)
    scale_up_cost = response.json()["score"]["cost_estimate"]
    
    # Scale down should have negative cost (savings)
    scale_down_data = {
        "proposal_id": "prop-cost-002", 
        "manifest": {
            "action": "scale_down",
            "parameters": {"target_count": 1}
        }
    }
    
    response = client.post("/score", json=scale_down_data)
    scale_down_cost = response.json()["score"]["cost_estimate"]
    
    assert scale_up_cost > 0
    assert scale_down_cost < 0

def test_batch_scoring():
    """Test batch scoring multiple proposals"""
    proposals = [
        {
            "proposal_id": "batch-001",
            "manifest": {"action": "scale_up", "target": "compute_instances"}
        },
        {
            "proposal_id": "batch-002",
            "manifest": {"action": "security_patch", "target": "system"}
        }
    ]
    
    response = client.post("/batch_score", json=proposals)
    assert response.status_code == 200
    data = response.json()
    
    assert "batch_results" in data
    assert len(data["batch_results"]) == 2
    assert data["total_processed"] == 2

def test_list_models():
    """Test listing available scoring models"""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    
    assert "models" in data
    assert len(data["models"]) > 0
    
    for model in data["models"]:
        assert "name" in model
        assert "version" in model
        assert "capabilities" in model

def test_confidence_factors():
    """Test that confidence factors are properly calculated"""
    score_data = {
        "proposal_id": "prop-factors-001",
        "manifest": {
            "action": "security_patch",
            "target": "system",
            "impact_level": "high",
            "rollback_plan": True,
            "approval_required": True,
            "safety_checks": ["backup", "test", "validate"]
        }
    }
    
    response = client.post("/score", json=score_data)
    data = response.json()
    
    factors = data["score"]["factors"]
    assert factors["action_type"] == "security_patch"
    assert factors["impact_level"] == "high"
    assert factors["rollback_available"] == True
    assert factors["approval_required"] == True
    assert factors["safety_checks"] == 3

if __name__ == "__main__":
    pytest.main([__file__])