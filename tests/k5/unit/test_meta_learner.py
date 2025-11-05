import unittest
import json
import os
from unittest.mock import patch, MagicMock

class TestMetaLearner(unittest.TestCase):
    
    def setUp(self):
        os.environ['SIMULATION_MODE'] = 'true'
        os.environ['SERVICE_PORT'] = '8800'
    
    @patch('requests.post')
    def test_learn_endpoint(self, mock_post):
        """Test meta-learner learn endpoint"""
        # Mock explainability response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"explain_id": "test-explain-123"}
        mock_post.return_value = mock_response
        
        # Import after setting env vars
        from services.meta_learner.src.main import app
        
        with app.test_client() as client:
            response = client.post('/v1/learn', json={})
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertIn('id', data)
            self.assertIn('confidence', data)
            self.assertIn('expected_gain', data)
            self.assertTrue(data['simulation_mode'])
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        from services.meta_learner.src.main import app
        
        with app.test_client() as client:
            response = client.get('/health')
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertEqual(data['status'], 'ok')
            self.assertTrue(data['simulation_mode'])

if __name__ == '__main__':
    unittest.main()