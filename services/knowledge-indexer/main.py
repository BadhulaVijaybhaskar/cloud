#!/usr/bin/env python3
"""
K.3 Knowledge Indexer - Logs incident → resolution patterns
Port: 8603
"""
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# Simulated knowledge base
KNOWLEDGE_BASE = [
    {
        'incident_type': 'service_crash',
        'action': 'restart_service',
        'success_rate': 0.95,
        'avg_recovery_time': 45,
        'occurrences': 23
    },
    {
        'incident_type': 'latency_spike',
        'action': 'scale_replicas',
        'success_rate': 0.88,
        'avg_recovery_time': 30,
        'occurrences': 15
    }
]

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'simulation_mode': SIMULATION_MODE})

@app.route('/v1/index', methods=['POST'])
def index_resolution():
    """Index incident resolution pattern"""
    data = request.get_json()
    
    if SIMULATION_MODE:
        pattern = {
            'incident_id': data.get('incident_id'),
            'incident_type': data.get('incident_type'),
            'action_taken': data.get('action_taken'),
            'success': data.get('success', True),
            'recovery_time': data.get('recovery_time', 60),
            'indexed_at': datetime.utcnow().isoformat(),
            'simulation': True
        }
        
        return jsonify({
            'status': 'indexed',
            'pattern': pattern
        })
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/knowledge')
def get_knowledge():
    """Get knowledge base patterns"""
    incident_type = request.args.get('type')
    
    if SIMULATION_MODE:
        if incident_type:
            patterns = [kb for kb in KNOWLEDGE_BASE if kb['incident_type'] == incident_type]
        else:
            patterns = KNOWLEDGE_BASE
        
        return jsonify({
            'patterns': patterns,
            'total': len(patterns),
            'simulation': True
        })
    
    return jsonify({'patterns': []})

@app.route('/v1/recommend', methods=['POST'])
def recommend_action():
    """Recommend action based on historical patterns"""
    data = request.get_json()
    incident_type = data.get('incident_type')
    
    if SIMULATION_MODE:
        # Find best action for incident type
        relevant_patterns = [kb for kb in KNOWLEDGE_BASE if kb['incident_type'] == incident_type]
        
        if relevant_patterns:
            best_pattern = max(relevant_patterns, key=lambda x: x['success_rate'])
            recommendation = {
                'recommended_action': best_pattern['action'],
                'confidence': best_pattern['success_rate'],
                'expected_recovery_time': best_pattern['avg_recovery_time'],
                'based_on_occurrences': best_pattern['occurrences'],
                'simulation': True
            }
        else:
            recommendation = {
                'recommended_action': 'restart_service',
                'confidence': 0.7,
                'expected_recovery_time': 60,
                'based_on_occurrences': 0,
                'simulation': True
            }
        
        return jsonify(recommendation)
    
    return jsonify({'error': 'Live mode not implemented'}), 501

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8603))
    app.run(host='0.0.0.0', port=port, debug=SIMULATION_MODE)