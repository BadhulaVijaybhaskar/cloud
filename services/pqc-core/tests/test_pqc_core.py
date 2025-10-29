import pytest
import requests

def test_pqc_core_health():
    response = requests.get("http://localhost:8601/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_pqc_encrypt():
    payload = {"message": "test_message", "algorithm": "kyber768"}
    response = requests.post("http://localhost:8601/pqc/encrypt", json=payload)
    assert response.status_code == 200

def test_pqc_keygen():
    response = requests.post("http://localhost:8601/pqc/keygen?algorithm=kyber768")
    assert response.status_code == 200