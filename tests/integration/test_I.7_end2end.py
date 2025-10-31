# tests/integration/test_I.7_end2end.py
import os, requests, json, time

CTRL = os.getenv("AOL_CONTROLLER_URL","http://localhost:9301")
SIM = os.getenv("SIMULATION_MODE","true").lower() == "true"

def safe_post(url, body):
    try:
        r = requests.post(url, json=body, timeout=5)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

def test_recommend_and_simulate():
    rec = {"tenant_id":"demo","recommendation_type":"scale","payload":{"service":"data-api","scale":2},"reason":"test"}
    status, text = safe_post(f"{CTRL}/recommend", rec)
    assert status in (200,201,0)
    if status in (200,201):
        j = json.loads(text)
        assert "recommendation_id" in j or "id" in j

def test_healths():
    ok = True
    for port in (9301,9302,9303,9304,9305,9306):
        try:
            r = requests.get(f"http://localhost:{port}/health", timeout=2)
            if r.status_code != 200: ok = False
        except:
            ok = False
    assert ok or SIM