#!/usr/bin/env python3
"""
Adaptive Scaler - Policy-driven scaling coordinator
Phase K.2 - Adaptive Scaling & Predictive Ops
"""

import os
import json
import time
import uuid
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
AOL_CONTROLLER_URL = os.getenv('AOL_CONTROLLER_URL', 'http://aol-controller:8200')
PREDICTIVE_ENGINE_URL = os.getenv('PREDICTIVE_ENGINE_URL', 'http://predictive-ops-engine:8500')

# Scaling thresholds
SCALE_UP_CPU_THRESHOLD = 0.75
SCALE_DOWN_CPU_THRESHOLD = 0.30
SCALE_UP_MEMORY_THRESHOLD = 0.80
SCALE_DOWN_MEMORY_THRESHOLD = 0.40
MAX_REPLICAS = 50
MIN_REPLICAS = 1

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "adaptive-scaler",
        "simulation_mode": SIMULATION_MODE
    })

@app.route('/v1/analyze', methods=['POST'])
def analyze():
    """Analyze metrics and generate scaling recommendations"""
    try:
        data = request.get_json()
        target = data.get('target')
        current_metrics = data.get('metrics', {})
        current_replicas = data.get('current_replicas', 1)
        
        # Get predictions from predictive engine
        predictions = get_predictions(target, current_metrics)
        
        # Generate scaling decision
        decision = make_scaling_decision(
            target, current_metrics, predictions, current_replicas
        )
        
        return jsonify(decision)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/execute', methods=['POST'])
def execute():
    """Execute scaling decision through AOL controller"""
    try:
        data = request.get_json()
        decision = data.get('decision')
        
        if not decision or decision.get('action') == 'no_action':
            return jsonify({"status": "no_action_required"})
        
        # Send decision to AOL controller
        result = send_to_controller(decision)
        
        return jsonify({
            "execution_id": str(uuid.uuid4()),
            "decision_sent": True,
            "controller_response": result,
            "simulation_mode": SIMULATION_MODE
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_predictions(target, metrics):
    """Get predictions from predictive ops engine"""
    try:
        response = requests.post(
            f"{PREDICTIVE_ENGINE_URL}/v1/forecast",
            json={"target": target, "metrics": metrics},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('predictions', {})
    except Exception:
        pass
    
    # Fallback to simple prediction
    return {
        "load": {
            "cpu_forecast": metrics.get('cpu_usage', 0.5) + 0.1,
            "memory_forecast": metrics.get('memory_usage', 0.4) + 0.05
        },
        "failure": {
            "failure_probability": 0.01
        }
    }

def make_scaling_decision(target, current_metrics, predictions, current_replicas):
    """Make scaling decision based on current metrics and predictions"""
    current_cpu = current_metrics.get('cpu_usage', 0.5)
    current_memory = current_metrics.get('memory_usage', 0.4)
    
    predicted_cpu = predictions.get('load', {}).get('cpu_forecast', current_cpu)
    predicted_memory = predictions.get('load', {}).get('memory_forecast', current_memory)
    failure_prob = predictions.get('failure', {}).get('failure_probability', 0.01)
    
    decision = {
        "id": str(uuid.uuid4()),
        "target": target,
        "timestamp": datetime.utcnow().isoformat(),
        "current_replicas": current_replicas,
        "current_metrics": current_metrics,
        "predictions": predictions,
        "action": "no_action",
        "recommended_replicas": current_replicas,
        "reasoning": []
    }
    
    # Scale up conditions
    if (predicted_cpu > SCALE_UP_CPU_THRESHOLD or 
        predicted_memory > SCALE_UP_MEMORY_THRESHOLD or
        failure_prob > 0.05):
        
        new_replicas = min(MAX_REPLICAS, current_replicas + 1)
        if new_replicas > current_replicas:
            decision.update({
                "action": "scale_up",
                "recommended_replicas": new_replicas,
                "reasoning": [
                    f"Predicted CPU: {predicted_cpu:.2f} > {SCALE_UP_CPU_THRESHOLD}",
                    f"Predicted Memory: {predicted_memory:.2f} > {SCALE_UP_MEMORY_THRESHOLD}",
                    f"Failure probability: {failure_prob:.3f}"
                ]
            })
    
    # Scale down conditions
    elif (predicted_cpu < SCALE_DOWN_CPU_THRESHOLD and 
          predicted_memory < SCALE_DOWN_MEMORY_THRESHOLD and
          failure_prob < 0.01):
        
        new_replicas = max(MIN_REPLICAS, current_replicas - 1)
        if new_replicas < current_replicas:
            decision.update({
                "action": "scale_down",
                "recommended_replicas": new_replicas,
                "reasoning": [
                    f"Predicted CPU: {predicted_cpu:.2f} < {SCALE_DOWN_CPU_THRESHOLD}",
                    f"Predicted Memory: {predicted_memory:.2f} < {SCALE_DOWN_MEMORY_THRESHOLD}",
                    f"Low failure probability: {failure_prob:.3f}"
                ]
            })
    
    return decision

def send_to_controller(decision):
    """Send scaling decision to AOL controller"""
    try:
        controller_payload = {
            "service": decision['target'],
            "cpu_usage": 85 if decision['action'] == 'scale_up' else 25,
            "memory_usage": 70,
            "predicted_action": decision['action'],
            "recommended_replicas": decision['recommended_replicas']
        }
        
        response = requests.post(
            f"{AOL_CONTROLLER_URL}/v1/decide",
            json=controller_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Controller returned {response.status_code}"}
    
    except Exception as e:
        return {"error": f"Failed to contact controller: {str(e)}"}

if __name__ == '__main__':
    print(f"Starting Adaptive Scaler on port 8501 (simulation: {SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=8501, debug=True)