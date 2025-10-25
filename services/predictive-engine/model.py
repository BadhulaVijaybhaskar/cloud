#!/usr/bin/env python3
"""
Predictive Intelligence Model
Simplified logistic regression for failure prediction without sklearn
"""

import math
import json
import logging

logger = logging.getLogger(__name__)

class PredictiveModel:
    """Lightweight ML model for failure prediction"""
    
    def __init__(self):
        self.is_trained = True  # Use pre-trained weights
        self.version = "v1.0"
        # Pre-trained weights for [cpu, memory, error_rate, response_time]
        self.weights = [0.3, 0.3, 0.3, 0.1]
        self.bias = -0.5
        
    def extract_features(self, metrics_data):
        """Extract numerical features from metrics/run data"""
        if not metrics_data:
            return [0.5, 0.5, 0.5, 0.5]
        
        # Extract key metrics
        cpu_usage = metrics_data.get('cpu_usage_percent', 50.0)
        memory_usage = metrics_data.get('memory_usage_percent', 50.0)
        error_rate = metrics_data.get('error_rate', 0.0)
        response_time = metrics_data.get('response_time_ms', 100.0)
        
        # Normalize to 0-1 range
        features = [
            min(cpu_usage / 100.0, 1.0),
            min(memory_usage / 100.0, 1.0), 
            min(error_rate / 100.0, 1.0),
            min(response_time / 1000.0, 1.0)
        ]
        
        return features
    
    def sigmoid(self, x):
        """Sigmoid activation function"""
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0
    
    def predict(self, metrics_data):
        """Predict failure probability and generate recommendations"""
        # Extract features
        features = self.extract_features(metrics_data)
        
        # Calculate linear combination
        linear_output = self.bias
        for i, feature in enumerate(features):
            linear_output += self.weights[i] * feature
        
        # Apply sigmoid to get probability
        probability = self.sigmoid(linear_output)
        
        # Generate recommendations based on probability and features
        recommendations = self.generate_recommendations(probability, metrics_data)
        
        return {
            'probability': float(probability),
            'model_version': self.version,
            'recommendations': recommendations
        }
    
    def generate_recommendations(self, probability, metrics_data):
        """Generate actionable recommendations based on prediction"""
        recommendations = {
            'risk_level': 'low',
            'actions': [],
            'rca_hints': []
        }
        
        if probability > 0.8:
            recommendations['risk_level'] = 'critical'
            recommendations['actions'] = [
                'Immediate investigation required',
                'Consider scaling resources',
                'Review recent deployments'
            ]
            recommendations['rca_hints'] = [
                'High resource utilization detected',
                'Check for memory leaks or CPU spikes'
            ]
        elif probability > 0.6:
            recommendations['risk_level'] = 'high'
            recommendations['actions'] = [
                'Monitor closely',
                'Prepare rollback plan',
                'Check system health'
            ]
            recommendations['rca_hints'] = [
                'Elevated metrics detected',
                'Review system performance trends'
            ]
        elif probability > 0.3:
            recommendations['risk_level'] = 'medium'
            recommendations['actions'] = [
                'Continue monitoring',
                'Review metrics trends'
            ]
        else:
            recommendations['risk_level'] = 'low'
            recommendations['actions'] = [
                'System operating normally'
            ]
        
        return recommendations