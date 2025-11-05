import unittest
import json
import os
from unittest.mock import patch, MagicMock

class TestFederationPolicyBroker(unittest.TestCase):
    
    def setUp(self):
        os.environ['SIMULATION_MODE'] = 'true'
        os.environ['SERVICE_PORT'] = '8903'
        os.environ['APPROVE_FEDERATION'] = 'no'
    
    def test_health_endpoint(self):
        """Test policy broker health endpoint"""
        from services.federation_policy_broker.src.main import app
        
        with app.test_client() as client:
            response = client.get('/health')
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertEqual(data['status'], 'healthy')
            self.assertTrue(data['simulation_mode'])
            self.assertFalse(data['approve_federation'])
    
    def test_validate_action_success(self):
        """Test successful action validation"""
        from services.federation_policy_broker.src.main import app
        
        with app.test_client() as client:
            action_data = {
                "action_type": "metadata_sync",
                "source_node": "node1",
                "target_nodes": ["node2"],
                "payload": {"type": "sanitized_metadata"}
            }
            
            response = client.post('/v1/validate', json=action_data)
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertTrue(data['allowed'])
            self.assertIn('audit_ref', data)
    
    def test_validate_action_p25_violation(self):
        """Test P25 policy violation detection"""
        from services.federation_policy_broker.src.main import app
        
        with app.test_client() as client:
            action_data = {
                "action_type": "data_sync",
                "source_node": "node1",
                "target_nodes": ["node2"],
                "payload": {"tenant_id": "12345", "user_data": "sensitive"}
            }
            
            response = client.post('/v1/validate', json=action_data)
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertFalse(data['allowed'])
            self.assertIn('P25 violation', str(data['reasons']))

if __name__ == '__main__':
    unittest.main()