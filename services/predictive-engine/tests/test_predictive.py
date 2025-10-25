#!/usr/bin/env python3
"""
Tests for Predictive Intelligence Engine
"""

import pytest
import json
import sys
import os
import tempfile
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from model import PredictiveModel
from server import PredictiveEngine

class TestPredictiveModel:
    """Test cases for predictive model"""
    
    def setup_method(self):
        """Setup test environment"""
        self.model = PredictiveModel()
    
    def test_model_initialization(self):
        """Test model initializes correctly"""
        assert self.model.version == "v1.0"
        assert self.model.is_trained
    
    def test_feature_extraction(self):
        """Test feature extraction from metrics"""
        metrics = {
            'cpu_usage_percent': 80.0,
            'memory_usage_percent': 60.0,
            'error_rate': 5.0,
            'response_time_ms': 200.0
        }
        
        features = self.model.extract_features(metrics)
        
        assert len(features) == 4
        assert all(0 <= f <= 1 for f in features)
    
    def test_prediction_probability_range(self):
        """Test prediction returns probability in valid range"""
        metrics = {
            'cpu_usage_percent': 75.0,
            'memory_usage_percent': 65.0,
            'error_rate': 2.0,
            'response_time_ms': 150.0
        }
        
        result = self.model.predict(metrics)
        
        assert 0.0 <= result['probability'] <= 1.0
        assert result['model_version'] == "v1.0"
        assert 'recommendations' in result
    
    def test_recommendations_structure(self):
        """Test recommendation structure is valid"""
        metrics = {'cpu_usage_percent': 90.0}
        result = self.model.predict(metrics)
        
        recommendations = result['recommendations']
        assert 'risk_level' in recommendations
        assert 'actions' in recommendations
        assert 'rca_hints' in recommendations
        assert recommendations['risk_level'] in ['low', 'medium', 'high', 'critical']

class TestPredictiveEngine:
    """Test cases for predictive engine service"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.engine = PredictiveEngine()
        self.engine.db_path = self.temp_db.name
        self.engine._init_db()
    
    def teardown_method(self):
        """Cleanup test environment"""
        import os
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass  # Ignore cleanup errors
    
    def test_prediction_storage(self):
        """Test prediction is stored correctly"""
        request_data = {
            'run_id': "test-run-123",
            'signal_id': "test-signal-456",
            'metrics_data': {'cpu_usage_percent': 70.0}
        }
        
        response = self.engine.predict(request_data)
        
        assert response['id'] is not None
        assert 0.0 <= response['probability'] <= 1.0
        assert response['model_version'] == "v1.0"
        assert response['recommendations'] is not None
    
    def test_get_predictions(self):
        """Test retrieving predictions"""
        # Create a prediction first
        request_data = {
            'run_id': "test-run-789",
            'metrics_data': {'memory_usage_percent': 80.0}
        }
        
        self.engine.predict(request_data)
        
        # Retrieve predictions
        predictions = self.engine.get_predictions(limit=10)
        
        assert len(predictions) >= 1
        assert predictions[0]['run_id'] == "test-run-789"
    
    def test_high_risk_prediction(self):
        """Test high-risk scenario generates appropriate recommendations"""
        request_data = {
            'metrics_data': {
                'cpu_usage_percent': 95.0,
                'memory_usage_percent': 90.0,
                'error_rate': 15.0,
                'response_time_ms': 800.0
            }
        }
        
        response = self.engine.predict(request_data)
        
        # High resource usage should generate higher probability
        assert response['probability'] > 0.3  # Should be elevated
        assert response['recommendations']['risk_level'] in ['medium', 'high', 'critical']

if __name__ == "__main__":
    pytest.main([__file__, "-v"])