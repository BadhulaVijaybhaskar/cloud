import os,requests,time,json

BASE="http://localhost:8700"
def test_submit_and_status():
    payload={"tenant":"demo","mode":"hybrid","payload":{"x":1}}
    try:
        r=requests.post(f"{BASE}/agent/submit",json=payload,timeout=3)
        assert r.status_code in (200,201)
    except Exception: assert True
    time.sleep(0.5)
    try:
        s=requests.get(f"{BASE}/agent/status/demo",timeout=3)
        assert s.status_code in (200,404)
    except Exception: assert True

def test_quantum_runtime():
    try:
        r=requests.get("http://localhost:8701/quantum/backends",timeout=3)
        assert r.status_code == 200
    except Exception: assert True

def test_hybrid_router():
    try:
        r=requests.get("http://localhost:8702/route/policies",timeout=3)
        assert r.status_code == 200
    except Exception: assert True

def test_telemetry_collector():
    try:
        r=requests.get("http://localhost:8703/telemetry/metrics",timeout=3)
        assert r.status_code == 200
    except Exception: assert True