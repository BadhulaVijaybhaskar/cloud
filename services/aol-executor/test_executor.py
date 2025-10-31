import pytest,json
from main import app

def test_health():
    with app.test_client() as c:
        r = c.get('/health')
        assert r.status_code == 200

def test_execute():
    with app.test_client() as c:
        r = c.post('/execute', json={'recommendation_id': 'test'})
        assert r.status_code == 200