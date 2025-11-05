#!/usr/bin/env python3
"""
K.4 Experience Repository - Stores and manages operational experiences
Port: 8701
"""
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# Simulated experience database
EXPERIENCE_DB = [
    {
        'id': 'exp-001',
        'type': 'scaling_pattern',
        'description': 'Efficient scaling for web services',
        'pattern': 'CPU > 80% for 5min → scale +2 replicas',
        'success_rate': 0.88,
        'confidence': 0.92,
        'origin': 'workspace-alpha',
        'anonymized': True,
        'created_at': '2024-12-19T16:00:00Z'
    },
    {
        'id': 'exp-002', 
        'type': 'incident_resolution',
        'description': 'Memory leak detection and resolution',
        'pattern': 'Memory leak + high latency → restart service',
        'success_rate': 0.94,
        'confidence': 0.95,
        'origin': 'workspace-beta',
        'anonymized': True,
        'created_at': '2024-12-19T15:30:00Z'
    }
]

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'simulation_mode': SIMULATION_MODE})

@app.route('/v1/experiences', methods=['POST'])
def store_experience():
    """Store operational experience"""
    data = request.get_json()
    
    if SIMULATION_MODE:
        experience = {
            'id': f"exp-{len(EXPERIENCE_DB) + 1:03d}",
            'type': data.get('type'),
            'description': data.get('description'),
            'pattern': data.get('pattern'),
            'success_rate': data.get('success_rate', 0.85),
            'confidence': data.get('confidence', 0.80),
            'origin': 'anonymized',
            'anonymized': True,
            'created_at': datetime.utcnow().isoformat(),
            'simulation': True
        }
        
        EXPERIENCE_DB.append(experience)
        return jsonify({'status': 'stored', 'experience': experience})
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/experiences')
def list_experiences():
    """List stored experiences"""
    experience_type = request.args.get('type')
    
    if SIMULATION_MODE:
        if experience_type:
            experiences = [exp for exp in EXPERIENCE_DB if exp['type'] == experience_type]
        else:
            experiences = EXPERIENCE_DB
        
        return jsonify({
            'experiences': experiences,
            'total': len(experiences),
            'simulation': True
        })
    
    return jsonify({'experiences': []})

@app.route('/v1/experiences/<exp_id>')
def get_experience(exp_id):
    """Get specific experience"""
    if SIMULATION_MODE:
        experience = next((exp for exp in EXPERIENCE_DB if exp['id'] == exp_id), None)
        if experience:
            return jsonify(experience)
        return jsonify({'error': 'Experience not found'}), 404
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/search', methods=['POST'])
def search_experiences():
    """Search experiences by criteria"""
    data = request.get_json()
    query = data.get('query', '')
    
    if SIMULATION_MODE:
        # Simple simulation search
        results = [exp for exp in EXPERIENCE_DB if query.lower() in exp['description'].lower()]
        
        return jsonify({
            'results': results,
            'total': len(results),
            'query': query,
            'simulation': True
        })
    
    return jsonify({'error': 'Live mode not implemented'}), 501

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8701))
    app.run(host='0.0.0.0', port=port, debug=SIMULATION_MODE)