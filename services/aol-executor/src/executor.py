#!/usr/bin/env python3
"""
AOL Executor - Execute approved autonomous actions
Phase K.1 - Autonomous Runtime Activation
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
NAMESPACE = os.getenv('NAMESPACE', 'atom-auto')

# Execution job store
jobs = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "aol-executor"})

@app.route('/v1/execute', methods=['POST'])
def execute():
    """Execute approved autonomous action"""
    try:
        data = request.get_json()
        action_id = data.get('action_id')
        action = data.get('action')
        
        job_id = str(uuid.uuid4())
        
        job = {
            "id": job_id,
            "action_id": action_id,
            "action": action,
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat(),
            "simulation_mode": SIMULATION_MODE
        }
        
        # Execute action
        if SIMULATION_MODE:
            job['status'] = 'simulated'
            job['result'] = simulate_action(action)
        else:
            job['status'] = 'executing'
            job['result'] = execute_action(action)
        
        jobs[job_id] = job
        return jsonify({"job_id": job_id, "status": job['status']})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get execution job status"""
    if job_id in jobs:
        return jsonify(jobs[job_id])
    return jsonify({"error": "Job not found"}), 404

def simulate_action(action):
    """Simulate action execution"""
    action_type = action.get('type')
    target = action.get('target')
    params = action.get('params', {})
    
    return {
        "simulated": True,
        "action_type": action_type,
        "target": target,
        "params": params,
        "message": f"Would execute {action_type} on {target}"
    }

def execute_action(action):
    """Execute real action"""
    action_type = action.get('type')
    target = action.get('target')
    params = action.get('params', {})
    
    try:
        if action_type == 'scale':
            return execute_scale(target, params)
        elif action_type == 'restart':
            return execute_restart(target, params)
        elif action_type == 'reroute':
            return execute_reroute(target, params)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    except Exception as e:
        return {"error": str(e)}

def execute_scale(target, params):
    """Execute scaling action"""
    replicas = params.get('replicas', 1)
    cmd = f"kubectl scale deployment {target} --replicas={replicas} -n {NAMESPACE}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    return {
        "action": "scale",
        "target": target,
        "replicas": replicas,
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr
    }

def execute_restart(target, params):
    """Execute restart action"""
    strategy = params.get('strategy', 'rolling')
    cmd = f"kubectl rollout restart deployment {target} -n {NAMESPACE}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    return {
        "action": "restart",
        "target": target,
        "strategy": strategy,
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr
    }

def execute_reroute(target, params):
    """Execute reroute action"""
    return {
        "action": "reroute",
        "target": target,
        "params": params,
        "message": "Reroute action simulated - would update service mesh routing"
    }

if __name__ == '__main__':
    print(f"Starting AOL Executor on port 8310 (simulation: {SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=8310, debug=True)