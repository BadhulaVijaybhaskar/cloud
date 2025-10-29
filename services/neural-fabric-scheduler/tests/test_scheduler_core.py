import pytest
import requests

def test_neural_scheduler_health():
    response = requests.get("http://localhost:8600/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_node_registration():
    payload = {"node_id": "test-node-1", "gpus": 4}
    response = requests.post("http://localhost:8600/node/register", json=payload)
    assert response.status_code == 200

def test_job_scheduling():
    payload = {"tenant_id": "test_tenant", "model_id": "test_model", "resources": {"gpu": 1}}
    response = requests.post("http://localhost:8600/schedule", json=payload)
    assert response.status_code == 200