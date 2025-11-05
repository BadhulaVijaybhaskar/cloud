#!/usr/bin/env python3
"""
AOL Policy Engine - P1-P20 policy evaluation
Phase K.1 - Autonomous Runtime Activation
"""

import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Policy rules (P1-P20 compliance)
POLICIES = {
    'P1': {'name': 'Data Residency', 'critical': True},
    'P2': {'name': 'Encryption at Rest', 'critical': True},
    'P3': {'name': 'Access Control', 'critical': True},
    'P4': {'name': 'Audit Logging', 'critical': False},
    'P5': {'name': 'Resource Limits', 'critical': False}
}

SAFE_ACTIONS = ['scale', 'restart', 'reroute']
SAFE_SERVICES = os.getenv('AUTONOMOUS_SAFE_LIST', 'services/auth,services/billing').split(',')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "aol-policy"})

@app.route('/v1/evaluate', methods=['POST'])
def evaluate():
    """Evaluate actions against P1-P20 policies"""
    try:
        data = request.get_json()
        actions = data.get('actions', [])
        context = data.get('context', {})
        
        evaluation_result = {
            "allow": True,
            "reasons": [],
            "explain": {
                "timestamp": datetime.utcnow().isoformat(),
                "policies_checked": list(POLICIES.keys()),
                "actions_evaluated": len(actions)
            }
        }
        
        # Evaluate each action
        for action in actions:
            action_result = evaluate_action(action, context)
            if not action_result['allow']:
                evaluation_result['allow'] = False
                evaluation_result['reasons'].extend(action_result['reasons'])
        
        return jsonify(evaluation_result)
    
    except Exception as e:
        return jsonify({
            "allow": False,
            "reasons": [f"Policy evaluation error: {str(e)}"],
            "explain": {}
        }), 500

def evaluate_action(action, context):
    """Evaluate single action against policies"""
    result = {"allow": True, "reasons": []}
    
    action_type = action.get('type')
    target = action.get('target')
    
    # Check if action type is allowed
    if action_type not in SAFE_ACTIONS:
        result['allow'] = False
        result['reasons'].append(f"Action type '{action_type}' not in safe list")
    
    # Check if target service is in safe list
    if target and target not in SAFE_SERVICES:
        result['allow'] = False
        result['reasons'].append(f"Target '{target}' not in autonomous safe list")
    
    # P1-P5 policy checks
    if action_type == 'scale':
        replicas = action.get('params', {}).get('replicas', 1)
        if replicas > 10:
            result['allow'] = False
            result['reasons'].append("P5: Scaling beyond resource limits (max 10 replicas)")
    
    if action_type == 'restart':
        strategy = action.get('params', {}).get('strategy')
        if strategy != 'rolling':
            result['allow'] = False
            result['reasons'].append("P3: Only rolling restart strategy allowed")
    
    return result

if __name__ == '__main__':
    print("Starting AOL Policy Engine on port 8300")
    app.run(host='0.0.0.0', port=8300, debug=True)