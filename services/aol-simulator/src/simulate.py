#!/usr/bin/env python3
"""
AOL Simulator - Generate synthetic events for testing
Phase K.1 - Autonomous Runtime Activation
"""

import os
import json
import uuid
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Simulation job store
simulation_jobs = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "aol-simulator"})

@app.route('/v1/run-scenario', methods=['POST'])
def run_scenario():
    """Run simulation scenario"""
    try:
        data = request.get_json()
        scenario = data.get('scenario', 'default')
        duration = data.get('duration', 300)
        
        job_id = str(uuid.uuid4())
        
        job = {
            "id": job_id,
            "scenario": scenario,
            "duration": duration,
            "status": "running",
            "start_time": datetime.utcnow().isoformat(),
            "events_generated": 0
        }
        
        simulation_jobs[job_id] = job
        
        # Start simulation in background thread
        thread = threading.Thread(target=run_simulation, args=(job_id, scenario, duration))
        thread.daemon = True
        thread.start()
        
        return jsonify({"job_id": job_id, "status": "started"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/jobs/<job_id>', methods=['GET'])
def get_simulation_job(job_id):
    """Get simulation job status"""
    if job_id in simulation_jobs:
        return jsonify(simulation_jobs[job_id])
    return jsonify({"error": "Job not found"}), 404

def run_simulation(job_id, scenario, duration):
    """Run simulation scenario in background"""
    job = simulation_jobs[job_id]
    
    try:
        if scenario == 'node-failure':
            simulate_node_failure(job, duration)
        elif scenario == 'high-load':
            simulate_high_load(job, duration)
        elif scenario == 'service-degradation':
            simulate_service_degradation(job, duration)
        else:
            simulate_default(job, duration)
        
        job['status'] = 'completed'
        job['end_time'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)

def simulate_node_failure(job, duration):
    """Simulate node failure scenario"""
    events = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Generate node failure event
        event = {
            "type": "node_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "node": f"node-{random.randint(1, 5)}",
            "severity": "high",
            "context": {
                "cpu_usage": random.uniform(90, 100),
                "memory_usage": random.uniform(85, 95),
                "disk_usage": random.uniform(80, 90)
            }
        }
        events.append(event)
        job['events_generated'] += 1
        
        # Send event to AOL controller (if available)
        send_event_to_controller(event)
        
        time.sleep(random.uniform(5, 15))
    
    job['events'] = events

def simulate_high_load(job, duration):
    """Simulate high load scenario"""
    events = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        event = {
            "type": "high_load",
            "timestamp": datetime.utcnow().isoformat(),
            "service": f"service-{random.randint(1, 3)}",
            "severity": "medium",
            "context": {
                "cpu_usage": random.uniform(80, 95),
                "memory_usage": random.uniform(70, 85),
                "request_rate": random.uniform(1000, 2000),
                "error_rate": random.uniform(0.05, 0.15)
            }
        }
        events.append(event)
        job['events_generated'] += 1
        
        send_event_to_controller(event)
        time.sleep(random.uniform(10, 30))
    
    job['events'] = events

def simulate_service_degradation(job, duration):
    """Simulate service degradation scenario"""
    events = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        event = {
            "type": "service_degradation",
            "timestamp": datetime.utcnow().isoformat(),
            "service": f"service-{random.randint(1, 3)}",
            "severity": "medium",
            "context": {
                "response_time": random.uniform(2000, 5000),
                "error_rate": random.uniform(0.1, 0.3),
                "availability": random.uniform(0.85, 0.95)
            }
        }
        events.append(event)
        job['events_generated'] += 1
        
        send_event_to_controller(event)
        time.sleep(random.uniform(15, 45))
    
    job['events'] = events

def simulate_default(job, duration):
    """Default simulation scenario"""
    events = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        event = {
            "type": "default",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Default simulation event",
            "context": {"simulation": True}
        }
        events.append(event)
        job['events_generated'] += 1
        
        time.sleep(30)
    
    job['events'] = events

def send_event_to_controller(event):
    """Send event to AOL controller for decision making"""
    try:
        import requests
        controller_url = os.getenv('AOL_CONTROLLER_URL', 'http://aol-controller:8200')
        requests.post(f"{controller_url}/v1/decide", json=event.get('context', {}), timeout=5)
    except Exception:
        pass  # Ignore errors in simulation

if __name__ == '__main__':
    print("Starting AOL Simulator on port 8320")
    app.run(host='0.0.0.0', port=8320, debug=True)