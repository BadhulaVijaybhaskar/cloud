#!/usr/bin/env python3
"""Tests for Proposal Composer"""

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
    assert data["service"] == "proposal-composer"

def test_compose_proposal():
    """Test proposal composition"""
    compose_data = {
        "context": "reduce cost",
        "tenant_id": "sim-tenant",
        "signals": {"current_cost": 1000, "target_reduction": 0.2}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/compose", json=compose_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "manifest" in data
    assert "signature" in data
    assert data["manifest"]["action"] == "scale_down"

def test_compose_with_template():
    """Test composition with template"""
    compose_data = {
        "context": "security update needed",
        "tenant_id": "sim-tenant",
        "template_name": "security_update",
        "signals": {}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/compose", json=compose_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["template_applied"] == "security_update"
    assert data["manifest"]["impact_level"] == "high"

def test_pii_redaction():
    """Test PII redaction in signals"""
    compose_data = {
        "context": "user data processing",
        "tenant_id": "sim-tenant",
        "signals": {
            "user_email": "test@example.com",
            "user_phone": "123-456-7890",
            "description": "Process user test@example.com data"
        }
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/compose", json=compose_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["pii_redacted"] == True

def test_list_templates():
    """Test template listing"""
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) > 0
    
    template_names = [t["name"] for t in data["templates"]]
    assert "cost_optimization" in template_names

def test_tenant_access_control():
    """Test tenant access control"""
    compose_data = {
        "context": "test",
        "tenant_id": "different-tenant",
        "signals": {}
    }
    
    headers = {"Authorization": "Bearer sim-token"}
    response = client.post("/compose", json=compose_data, headers=headers)
    
    assert response.status_code == 403

if __name__ == "__main__":
    pytest.main([__file__])