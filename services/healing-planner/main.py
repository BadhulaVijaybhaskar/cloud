#!/usr/bin/env python3
"""
K.3 Healing Planner - Chooses remediation plan & action priority
Port: 8601
"""
import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# Healing strategies by incident type
HEALING_STRATEGIES = {
    'service_crash': [
        {'action': 'restart_service', 'priority': 1, 'risk': 'low'},
        {'action': 'scale_replicas', 'priority': 2, 'risk': 'medium'},
        {'action': 'reroute_traffic', 'priority': 3, 'risk': 'high'}
    ],
    'latency_spike': [
        {'action': 'scale_replicas', 'priority': 1, 'risk': 'low'},
        {'action': 'restart_service', 'priority': 2, 'risk': 'medium'}
    ],
    'memory_leak': [
        {'action': 'restart_service', 'priority': 1, 'risk': 'low'},
        {'action': 'reduce_load', 'priority': 2, 'risk': 'medium'}
    ],
    'disk_full': [
        {'action': 'cleanup_logs', 'priority': 1, 'risk': 'low'},
        {'action': 'scale_storage', 'priority': 2, 'risk': 'medium'}
    ]
}

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'simulation_mode': SIMULATION_MODE})

@app.route('/v1/plan', methods=['POST'])
def create_healing_plan():
    """Create healing plan for incident"""
    data = request.get_json()
    incident_type = data.get('type', 'service_crash')
    severity = data.get('severity', 'medium')
    
    if SIMULATION_MODE:
        strategies = HEALING_STRATEGIES.get(incident_type, HEALING_STRATEGIES['service_crash'])
        
        # Filter by risk level based on severity
        if severity == 'low':
            strategies = [s for s in strategies if s['risk'] in ['low']]
        elif severity == 'medium':
            strategies = [s for s in strategies if s['risk'] in ['low', 'medium']]
        
        plan = {
            'incident_id': data.get('incident_id'),
            'strategies': strategies,
            'recommended_action': strategies[0] if strategies else None,
            'estimated_duration': 60,
            'requires_approval': severity == 'high',
            'simulation': True
        }
        
        return jsonify(plan)
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/plans/<plan_id>/approve', methods=['POST'])
def approve_plan(plan_id):
    """Approve healing plan"""
    if SIMULATION_MODE:
        return jsonify({
            'plan_id': plan_id,
            'status': 'approved',
            'approved_at': '2024-12-19T16:00:00Z',
            'simulation': True
        })
    
    return jsonify({'error': 'Live mode not implemented'}), 501

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8601))
    app.run(host='0.0.0.0', port=port, debug=SIMULATION_MODE)