import pytest,json
from main import app

def test_health():
    with app.test_client() as c:
        r = c.get('/health')
        assert r.status_code == 200

def test_evaluate():
    with app.test_client() as c:
        r = c.post('/evaluate', json={'recommendation_id': 'test'})
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['decision']['allowed'] == True