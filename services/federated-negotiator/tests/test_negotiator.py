#!/usr/bin/env python3
"""Tests for Federated Negotiator"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "federated-negotiator"

def test_start_negotiation():
    """Test starting a negotiation"""
    negotiation_data = {
        "proposal_id": "prop-test-001",
        "regions": ["us-east-1", "eu-west-1"],
        "quorum_threshold": 0.6
    }
    
    response = client.post("/negotiate", json=negotiation_data)
    assert response.status_code == 200
    data = response.json()
    assert "negotiation_id" in data
    assert data["status"] == "active"
    assert data["regions"] == ["us-east-1", "eu-west-1"]

def test_get_negotiation_status():
    """Test getting negotiation status"""
    # Start negotiation first
    negotiation_data = {
        "proposal_id": "prop-test-002",
        "regions": ["us-east-1", "eu-west-1"]
    }
    
    start_response = client.post("/negotiate", json=negotiation_data)
    negotiation_id = start_response.json()["negotiation_id"]
    
    # Get status
    response = client.get(f"/negotiate/{negotiation_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert "negotiation" in data
    assert "votes" in data
    assert "progress" in data

def test_submit_regional_vote():
    """Test submitting a regional vote"""
    # Start negotiation first
    negotiation_data = {
        "proposal_id": "prop-test-003",
        "regions": ["us-east-1", "eu-west-1"]
    }
    
    start_response = client.post("/negotiate", json=negotiation_data)
    negotiation_id = start_response.json()["negotiation_id"]
    
    # Submit vote
    vote_data = {
        "region": "us-east-1",
        "vote": "approve",
        "weight": 1.0,
        "reasoning": "Test approval"
    }
    
    response = client.post(f"/negotiate/{negotiation_id}/vote", json=vote_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "vote_recorded"

def test_consensus_calculation():
    """Test consensus calculation with multiple votes"""
    # Start negotiation
    negotiation_data = {
        "proposal_id": "prop-test-004",
        "regions": ["us-east-1", "eu-west-1"],
        "quorum_threshold": 0.5
    }
    
    start_response = client.post("/negotiate", json=negotiation_data)
    negotiation_id = start_response.json()["negotiation_id"]
    
    # Submit approving vote
    vote1_data = {
        "region": "us-east-1",
        "vote": "approve",
        "weight": 1.0
    }
    client.post(f"/negotiate/{negotiation_id}/vote", json=vote1_data)
    
    # Submit rejecting vote
    vote2_data = {
        "region": "eu-west-1", 
        "vote": "reject",
        "weight": 1.0
    }
    client.post(f"/negotiate/{negotiation_id}/vote", json=vote2_data)
    
    # Check final status
    response = client.get(f"/negotiate/{negotiation_id}/status")
    data = response.json()
    assert data["consensus_info"]["consensus_ratio"] == 0.5
    assert data["negotiation"]["status"] in ["consensus_reached", "consensus_failed"]

def test_negotiation_not_found():
    """Test getting status for non-existent negotiation"""
    response = client.get("/negotiate/non-existent/status")
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__])