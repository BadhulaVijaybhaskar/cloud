import pytest,json
from main import app

def test_health():
    with app.test_client() as c:
        r = c.get('/health')
        assert r.status_code == 200
        assert json.loads(r.data)['service'] == 'aol-simulator'

def test_simulate():
    with app.test_client() as c:
        r = c.post('/simulate', json={'recommendation_id': 'test'})
        assert r.status_code == 200
        data = json.loads(r.data)
        assert 'result' in data