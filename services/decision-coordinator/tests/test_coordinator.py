#!/usr/bin/env python3
"""Tests for Decision Coordinator"""

import pytest
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "decision-coordinator"

def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200

def test_submit_proposal():
    """Test proposal submission"""
    proposal_data = {
        "tenant_id": "sim-tenant",
        "manifest": {
            "action": "scale",
            "target": "serviceX",
            "impact_level": "medium"
        },
        "metadata": {"source": "test"}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/proposals", json=proposal_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "proposal_id" in data
    assert data["status"] == "submitted"
    assert "pre_state_hash" in data

def test_get_proposal_status():
    """Test getting proposal status"""
    # First submit a proposal
    proposal_data = {
        "tenant_id": "sim-tenant", 
        "manifest": {"action": "test"},
        "metadata": {}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    submit_response = client.post("/proposals", json=proposal_data, headers=headers)
    proposal_id = submit_response.json()["proposal_id"]
    
    # Then get its status
    response = client.get(f"/proposals/{proposal_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "proposal" in data
    assert data["proposal"]["proposal_id"] == proposal_id

def test_enact_proposal():
    """Test proposal enactment"""
    # Submit proposal first
    proposal_data = {
        "tenant_id": "sim-tenant",
        "manifest": {"action": "test", "impact_level": "low"},
        "metadata": {}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    submit_response = client.post("/proposals", json=proposal_data, headers=headers)
    proposal_id = submit_response.json()["proposal_id"]
    
    # Enact it
    enact_data = {
        "approver_id": "test-approver",
        "justification": "Test enactment"
    }
    
    response = client.post(f"/proposals/{proposal_id}/enact", json=enact_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "enacted"
    assert "post_state_hash" in data

def test_high_impact_requires_approver():
    """Test that high impact decisions require approver"""
    # Submit high impact proposal
    proposal_data = {
        "tenant_id": "sim-tenant",
        "manifest": {"action": "delete", "impact_level": "high"},
        "metadata": {}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    submit_response = client.post("/proposals", json=proposal_data, headers=headers)
    proposal_id = submit_response.json()["proposal_id"]
    
    # Try to enact without approver
    response = client.post(f"/proposals/{proposal_id}/enact", json={}, headers=headers)
    assert response.status_code == 400
    assert "approver" in response.json()["detail"].lower()

if __name__ == "__main__":
    pytest.main([__file__])