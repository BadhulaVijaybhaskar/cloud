import pytest
import requests

def test_vault_health():
    response = requests.get("http://localhost:8301/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_store_secret():
    payload = {"path": "test/secret", "data": {"key": "value"}}
    response = requests.post("http://localhost:8301/secrets", json=payload)
    assert response.status_code == 200

def test_get_secret():
    response = requests.get("http://localhost:8301/secrets/test/secret")
    assert response.status_code == 200