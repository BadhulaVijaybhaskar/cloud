import pytest
import requests

BASE_URLS = {
    "registry": "http://localhost:8401",
    "sync": "http://localhost:8402",
    "edge": "http://localhost:8403", 
    "tenant": "http://localhost:8404",
    "recovery": "http://localhost:8405",
    "policy": "http://localhost:8406"
}

def test_all_federation_services_healthy():
    """Test all G.1 federation services are healthy"""
    for service, url in BASE_URLS.items():
        response = requests.get(f"{url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

def test_region_registry():
    """Test region registration and listing"""
    response = requests.get(f"{BASE_URLS['registry']}/region/list")
    assert response.status_code == 200
    data = response.json()
    assert "regions" in data

def test_federation_sync():
    """Test cross-region sync status"""
    response = requests.get(f"{BASE_URLS['sync']}/sync/status")
    assert response.status_code == 200

def test_edge_routing():
    """Test geo-aware routing"""
    payload = {"user_location": "US", "service": "api"}
    response = requests.post(f"{BASE_URLS['edge']}/route", json=payload)
    assert response.status_code == 200

def test_tenant_replication():
    """Test tenant data replication"""
    response = requests.get(f"{BASE_URLS['tenant']}/tenant/test-tenant/status")
    assert response.status_code == 200

def test_disaster_recovery():
    """Test backup validation"""
    response = requests.get(f"{BASE_URLS['recovery']}/recovery/validate")
    assert response.status_code == 200

def test_federation_trust():
    """Test trust establishment"""
    response = requests.get(f"{BASE_URLS['policy']}/trust/status")
    assert response.status_code == 200