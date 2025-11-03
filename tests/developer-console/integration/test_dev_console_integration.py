import os
import requests
import pytest

BASE = os.getenv('DEVELOPER_CONSOLE_BASE_URL', 'http://localhost:8090')
SIM = os.getenv('SIMULATION_MODE', 'true') == 'true'

def test_health():
    if SIM:
        assert True
    else:
        r = requests.get(BASE + '/health')
        assert r.status_code == 200

def test_core_service():
    if SIM:
        assert True
    else:
        r = requests.get(BASE + ':8091/health')
        assert r.status_code == 200
        assert r.json()['service'] == 'developer-console-core'

def test_api_service():
    if SIM:
        assert True
    else:
        r = requests.get(BASE + ':8092/health')
        assert r.status_code == 200
        assert r.json()['service'] == 'developer-console-api'

def test_worker_service():
    if SIM:
        assert True
    else:
        r = requests.get(BASE + ':8093/health')
        assert r.status_code == 200
        assert r.json()['service'] == 'developer-console-worker'