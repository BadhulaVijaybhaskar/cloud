import pytest
import requests

BASE_URLS = {
    "vault": "http://localhost:8301",
    "cosign": "http://localhost:8302", 
    "audit": "http://localhost:8303",
    "kms": "http://localhost:8304",
    "pqc": "http://localhost:8305",
    "policy": "http://localhost:8306"
}

def test_all_security_services_healthy():
    """Test all F.7 security services are healthy"""
    for service, url in BASE_URLS.items():
        response = requests.get(f"{url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

def test_vault_operations():
    """Test vault secret operations"""
    payload = {"path": "test/secret", "data": {"key": "value"}}
    response = requests.post(f"{BASE_URLS['vault']}/secrets", json=payload)
    assert response.status_code == 200

def test_cosign_operations():
    """Test cosign signing operations"""
    payload = {"payload": "test data", "signer": "test@atom.cloud"}
    response = requests.post(f"{BASE_URLS['cosign']}/sign", json=payload)
    assert response.status_code == 200

def test_audit_logging():
    """Test audit pipeline logging"""
    payload = {"service": "test", "operation": "test_op"}
    response = requests.post(f"{BASE_URLS['audit']}/audit", json=payload)
    assert response.status_code == 200

def test_policy_enforcement():
    """Test policy gatekeeper enforcement"""
    response = requests.get(f"{BASE_URLS['policy']}/policy/status")
    assert response.status_code == 200
    data = response.json()
    assert "policies" in data

def test_pqc_keygen():
    """Test PQC key generation"""
    payload = {"algorithm": "kyber768", "purpose": "encryption"}
    response = requests.post(f"{BASE_URLS['pqc']}/pqc/keygen", json=payload)
    assert response.status_code == 200