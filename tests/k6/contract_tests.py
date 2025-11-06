import os, requests, pytest, json, time

ORCH = os.getenv("ORCHESTRATOR_URL","http://localhost:8900")
GATE = os.getenv("GATEWAY_URL","http://localhost:8901")
META = os.getenv("METADATA_URL","http://localhost:8902")
POLBRO = os.getenv("POLICY_BROKER_URL","http://localhost:8903")

@pytest.mark.timeout(5)
def test_health_endpoints():
    for base in (ORCH,GATE,META,POLBRO):
        r = requests.get(f"{base}/health", timeout=4)
        assert r.status_code == 200
        j = r.json()
        assert 'status' in j

def test_policy_broker_validate_shape():
    url = f"{POLBRO}/v1/validate"
    payload = {"action":"scale","target":"services/web","policy_context":{}}
    r = requests.post(url, json=payload, timeout=5)
    assert r.status_code in (200,202,400,422)
    try:
        resp = r.json()
        assert isinstance(resp, dict)
        assert 'allowed' in resp or 'simulated' in resp
    except ValueError:
        pytest.skip("policy broker returned non-json (likely simulation)")

def test_metadata_sanitize_shape():
    url = f"{META}/sanitize"
    payload = {"tenant_id":"t-1","region":"eu-west-1","meta":{"pii":"secret"}}
    r = requests.post(url, json=payload, timeout=5)
    assert r.status_code in (200,202,400)
    try:
        resp = r.json()
        assert isinstance(resp, dict)
    except ValueError:
        pytest.skip("metadata service returned non-json in simulation")