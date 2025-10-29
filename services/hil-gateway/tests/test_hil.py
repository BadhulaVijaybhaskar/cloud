#!/usr/bin/env python3
"""Tests for Human-in-Loop Gateway"""

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
    assert data["service"] == "hil-gateway"

def test_approve_proposal():
    """Test approving a proposal"""
    approval_data = {
        "proposal_id": "prop-test-001",
        "approver_id": "sim-user",
        "decision": "approve",
        "reason": "Test approval",
        "mfa_token": "mfa-sim-user-valid"
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/approve/prop-test-001", json=approval_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["approver"] == "sim-user"
    assert data["mfa_verified"] == True
    assert "signature" in data

def test_reject_proposal():
    """Test rejecting a proposal"""
    approval_data = {
        "proposal_id": "prop-test-002",
        "approver_id": "sim-user",
        "decision": "reject",
        "reason": "Security concerns"
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/approve/prop-test-002", json=approval_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"

def test_get_pending_approvals():
    """Test getting pending approvals for tenant"""
    headers = {"Authorization": "Bearer sim-token"}
    response = client.get("/pending/sim-tenant", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "pending_approvals" in data
    assert "total_pending" in data
    assert data["tenant_id"] == "sim-tenant"

def test_send_notification():
    """Test sending approval notifications"""
    notification_data = {
        "proposal_id": "prop-notify-001",
        "approvers": ["admin-001", "security-lead"],
        "channels": ["email", "slack"],
        "urgency": "high"
    }
    
    response = client.post("/notify", json=notification_data)
    assert response.status_code == 200
    data = response.json()
    assert "notifications_sent" in data
    assert "results" in data

def test_approval_history():
    """Test getting approval history"""
    # First approve a proposal
    approval_data = {
        "proposal_id": "prop-history-001",
        "approver_id": "sim-user",
        "decision": "approve",
        "reason": "Test for history"
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    client.post("/approve/prop-history-001", json=approval_data, headers=headers)
    
    # Then get its history
    response = client.get("/approval/prop-history-001/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "approvals" in data
    assert len(data["approvals"]) > 0

def test_mfa_verification():
    """Test MFA token verification"""
    # Valid MFA token
    approval_data = {
        "proposal_id": "prop-mfa-001",
        "approver_id": "sim-user",
        "decision": "approve",
        "mfa_token": "mfa-sim-user-valid"
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/approve/prop-mfa-001", json=approval_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["mfa_verified"] == True
    
    # Invalid MFA token
    approval_data["mfa_token"] = "invalid-token"
    approval_data["proposal_id"] = "prop-mfa-002"
    
    response = client.post("/approve/prop-mfa-002", json=approval_data, headers=headers)
    assert response.status_code == 400

def test_approver_id_mismatch():
    """Test approver ID validation"""
    approval_data = {
        "proposal_id": "prop-mismatch-001",
        "approver_id": "different-user",  # Different from token user
        "decision": "approve"
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/approve/prop-mismatch-001", json=approval_data, headers=headers)
    assert response.status_code == 403

def test_tenant_access_control():
    """Test tenant access control for pending approvals"""
    headers = {"Authorization": "Bearer sim-token"}
    response = client.get("/pending/different-tenant", headers=headers)
    assert response.status_code == 403

if __name__ == "__main__":
    pytest.main([__file__])