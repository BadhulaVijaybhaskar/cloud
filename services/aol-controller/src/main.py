#!/usr/bin/env python3
"""
AOL Controller - Central coordination and decision composer
Phase K.1 - Autonomous Runtime Activation
"""

import os
import json
import time
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import requests
import yaml

app = Flask(__name__)

# Configuration
CONFIG = {
    'SERVICE_NAME': os.getenv('SERVICE_NAME', 'aol-controller'),
    'PORT': int(os.getenv('PORT', 8200)),
    'POLICY_ENGINE_URL': os.getenv('AOL_POLICY_ENGINE_URL', 'http://aol-policy:8300'),
    'SIMULATION_MODE': os.getenv('SIMULATION_MODE', 'true').lower() == 'true',
    'AUTONOMOUS_MODE': os.getenv('AUTONOMOUS_MODE', 'false').lower() == 'true'
}

# In-memory decision store
decisions = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": CONFIG['SERVICE_NAME']})

@app.route('/v1/decide', methods=['POST'])
def decide():
    """Central decision endpoint - analyzes context and returns decisions"""
    try:
        context = request.get_json()
        decision_id = str(uuid.uuid4())
        
        # Generate decision based on context
        decision = {
            "id": decision_id,
            "actions": generate_actions(context),
            "score": calculate_decision_score(context),
            "timestamp": datetime.utcnow().isoformat(),
            "simulation_mode": CONFIG['SIMULATION_MODE']
        }
        
        # Store decision
        decisions[decision_id] = decision
        
        # If not simulation mode, evaluate with policy engine
        if not CONFIG['SIMULATION_MODE']:
            policy_result = evaluate_with_policy_engine(decision)
            decision['policy_evaluation'] = policy_result
        
        return jsonify(decision)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/decisions/<decision_id>', methods=['GET'])
def get_decision(decision_id):
    """Get decision status by ID"""
    if decision_id in decisions:
        return jsonify(decisions[decision_id])
    return jsonify({"error": "Decision not found"}), 404

def generate_actions(context):
    """Generate actions based on context"""
    actions = []
    
    # Example decision logic
    if context.get('cpu_usage', 0) > 80:
        actions.append({
            "type": "scale",
            "target": context.get('service', 'unknown'),
            "params": {"replicas": context.get('current_replicas', 1) + 1}
        })
    
    if context.get('error_rate', 0) > 0.1:
        actions.append({
            "type": "restart",
            "target": context.get('service', 'unknown'),
            "params": {"strategy": "rolling"}
        })
    
    return actions

def calculate_decision_score(context):
    """Calculate confidence score for decision"""
    score = 0.5  # baseline
    
    if context.get('cpu_usage'):
        score += 0.2
    if context.get('memory_usage'):
        score += 0.2
    if context.get('error_rate') is not None:
        score += 0.1
    
    return min(score, 1.0)

def evaluate_with_policy_engine(decision):
    """Evaluate decision with policy engine"""
    try:
        response = requests.post(
            f"{CONFIG['POLICY_ENGINE_URL']}/v1/evaluate",
            json={"action": decision["actions"], "context": {}},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"allow": False, "reasons": [f"Policy evaluation failed: {str(e)}"]}

if __name__ == '__main__':
    print(f"Starting {CONFIG['SERVICE_NAME']} on port {CONFIG['PORT']}")
    print(f"Simulation mode: {CONFIG['SIMULATION_MODE']}")
    app.run(host='0.0.0.0', port=CONFIG['PORT'], debug=True)