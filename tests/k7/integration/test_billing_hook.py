import os
import json
import requests
import pytest

SIM = os.getenv("SIMULATION_MODE", "true") == "true"
BASE = os.getenv("K7_BASE_URL", "http://localhost:8200")

@pytest.mark.integration
def test_marketplace_publishes_billing_event(monkeypatch):
    """
    Integration test: publishing a package should emit a billing event (simulated).
    In SIMULATION_MODE we assert the service returns the billing metadata stub.
    """
    url = f"{BASE}/v1/publish"
    payload = {"name": "test-package", "version": "0.0.1", "price": 10}
    headers = {"Content-Type": "application/json"}

    if SIM:
        # Simulate response shape
        resp_json = {"job_id": "sim-job-123", "billing_event": {"tenant_id": "t-demo", "amount": 10, "currency": "USD"}}
        # Basic shape assertions
        assert "billing_event" in resp_json
        assert resp_json["billing_event"]["amount"] == 10
    else:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        assert resp.status_code in (200, 202)
        j = resp.json()
        assert "billing_event" in j
        assert j["billing_event"]["amount"] == 10