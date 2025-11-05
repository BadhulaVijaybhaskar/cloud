import unittest
import json
import os
from unittest.mock import patch, MagicMock

class TestFederationOrchestrator(unittest.TestCase):
    
    def setUp(self):
        os.environ['SIMULATION_MODE'] = 'true'
        os.environ['SERVICE_PORT'] = '8900'
    
    def test_health_endpoint(self):
        """Test orchestrator health endpoint"""
        from services.federation_orchestrator.src.main import app
        
        with app.test_client() as client:
            response = client.get('/health')
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertEqual(data['status'], 'healthy')
            self.assertTrue(data['simulation_mode'])
    
    def test_register_node(self):
        """Test node registration"""
        from services.federation_orchestrator.src.main import app
        
        with app.test_client() as client:
            node_data = {
                "region": "us-west-1",
                "endpoint": "https://node1.example.com",
                "opt_in_status": True
            }
            
            response = client.post('/v1/register-node', json=node_data)
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertIn('node_id', data)
            self.assertEqual(data['status'], 'registered')
    
    def test_propose_action(self):
        """Test cross-region action proposal"""
        from services.federation_orchestrator.src.main import app
        
        with app.test_client() as client:
            proposal_data = {
                "action_type": "metadata_sync",
                "source_node": "node1",
                "target_nodes": ["node2", "node3"],
                "payload": {"type": "model_metadata"}
            }
            
            response = client.post('/v1/propose-action', json=proposal_data)
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertIn('proposal_id', data)
            self.assertEqual(data['status'], 'submitted')

if __name__ == '__main__':
    unittest.main()