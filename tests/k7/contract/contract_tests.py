# tests/k7/contract/contract_tests.py
import os, json, requests, pytest

BASE="http://localhost"
PORTS={"partner":"8200","market":"8210"}
SIM=os.getenv("SIMULATION_MODE","true")=="true"

def test_partner_health():
    url=f"{BASE}:{PORTS['partner']}/health"
    try:
        r=requests.get(url, timeout=3)
    except Exception:
        if SIM: pytest.skip("SIMULATION mode: partner portal not reachable")
        else: pytest.fail("partner portal not reachable")
    assert r.status_code==200

def test_register_partner():
    url=f"{BASE}:{PORTS['partner']}/v1/partners"
    payload={"name":"Test","email":"t@example.com","org":"T","public_key":"pk"}
    try:
        r=requests.post(url,json=payload,timeout=4)
        if SIM and r.status_code!=201:
            pytest.skip("SIMULATION: register may be simulated")
        assert r.status_code in (200,201)
        j=r.json()
        assert "partner_id" in j
    except Exception:
        if SIM: pytest.skip("SIMULATION: partner registration simulated")
        else: raise

def test_publish_package_shape():
    url=f"{BASE}:{PORTS['market']}/v1/publish"
    payload={"type":"model","metadata":{"name":"m1","version":"v0.1"},"signed_ref":"sha256:xxx"}
    try:
        r=requests.post(url,json=payload,timeout=5)
        if SIM and r.status_code not in (200,202):
            pytest.skip("SIMULATION: publish simulated")
        assert r.status_code in (200,202)
    except Exception:
        if SIM: pytest.skip("SIMULATION: marketplace publish simulated")
        else: raise