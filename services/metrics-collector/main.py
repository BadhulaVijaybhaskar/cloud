#!/usr/bin/env python3
"""
Metrics Collector - Unified metrics feed for predictive ops
Phase K.2 - Adaptive Scaling & Predictive Ops
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# Mock metrics storage
metrics_store = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "metrics-collector",
        "simulation_mode": SIMULATION_MODE
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-style metrics endpoint"""
    # Generate mock Prometheus metrics
    metrics_text = f"""# HELP aol_controller_requests_total Total requests to AOL controller
# TYPE aol_controller_requests_total counter
aol_controller_requests_total 123

# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total {random.uniform(0.1, 0.5)}

# HELP service_cpu_usage Current CPU usage ratio
# TYPE service_cpu_usage gauge
service_cpu_usage{{service="web"}} {random.uniform(0.3, 0.8)}
service_cpu_usage{{service="worker"}} {random.uniform(0.2, 0.6)}
service_cpu_usage{{service="db"}} {random.uniform(0.4, 0.9)}

# HELP service_memory_usage Current memory usage ratio
# TYPE service_memory_usage gauge
service_memory_usage{{service="web"}} {random.uniform(0.4, 0.7)}
service_memory_usage{{service="worker"}} {random.uniform(0.3, 0.5)}
service_memory_usage{{service="db"}} {random.uniform(0.5, 0.8)}

# HELP service_error_rate Current error rate
# TYPE service_error_rate gauge
service_error_rate{{service="web"}} {random.uniform(0.001, 0.05)}
service_error_rate{{service="worker"}} {random.uniform(0.001, 0.02)}
service_error_rate{{service="db"}} {random.uniform(0.001, 0.01)}

# HELP service_response_time_ms Average response time in milliseconds
# TYPE service_response_time_ms gauge
service_response_time_ms{{service="web"}} {random.uniform(50, 200)}
service_response_time_ms{{service="worker"}} {random.uniform(100, 500)}
service_response_time_ms{{service="db"}} {random.uniform(10, 50)}
"""
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/v1/collect', methods=['POST'])
def collect():
    """Collect metrics from services"""
    try:
        data = request.get_json()
        service = data.get('service')
        metrics = data.get('metrics', {})
        
        # Store metrics with timestamp
        timestamp = datetime.utcnow().isoformat()
        if service not in metrics_store:
            metrics_store[service] = []
        
        metrics_entry = {
            "timestamp": timestamp,
            "metrics": metrics
        }
        
        metrics_store[service].append(metrics_entry)
        
        # Keep only last 100 entries per service
        if len(metrics_store[service]) > 100:
            metrics_store[service] = metrics_store[service][-100:]
        
        return jsonify({
            "status": "collected",
            "service": service,
            "timestamp": timestamp
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/query', methods=['GET'])
def query():
    """Query collected metrics"""
    service = request.args.get('service')
    limit = int(request.args.get('limit', 10))
    
    if service and service in metrics_store:
        recent_metrics = metrics_store[service][-limit:]
        return jsonify({
            "service": service,
            "metrics": recent_metrics,
            "count": len(recent_metrics)
        })
    elif not service:
        # Return summary of all services
        summary = {}
        for svc, data in metrics_store.items():
            if data:
                latest = data[-1]
                summary[svc] = {
                    "latest_timestamp": latest["timestamp"],
                    "latest_metrics": latest["metrics"],
                    "total_entries": len(data)
                }
        return jsonify(summary)
    else:
        return jsonify({"error": "Service not found"}), 404

@app.route('/v1/aggregate', methods=['GET'])
def aggregate():
    """Get aggregated metrics for predictive analysis"""
    service = request.args.get('service')
    hours = int(request.args.get('hours', 1))
    
    if not service or service not in metrics_store:
        return jsonify({"error": "Service not found"}), 404
    
    # Get metrics from last N hours
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    recent_data = []
    
    for entry in metrics_store[service]:
        entry_time = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
        if entry_time >= cutoff_time:
            recent_data.append(entry)
    
    if not recent_data:
        return jsonify({
            "service": service,
            "hours": hours,
            "aggregated_metrics": {},
            "sample_count": 0
        })
    
    # Calculate aggregations
    cpu_values = [d["metrics"].get("cpu_usage", 0) for d in recent_data]
    memory_values = [d["metrics"].get("memory_usage", 0) for d in recent_data]
    error_values = [d["metrics"].get("error_rate", 0) for d in recent_data]
    
    aggregated = {
        "cpu_usage": {
            "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "max": max(cpu_values) if cpu_values else 0,
            "min": min(cpu_values) if cpu_values else 0
        },
        "memory_usage": {
            "avg": sum(memory_values) / len(memory_values) if memory_values else 0,
            "max": max(memory_values) if memory_values else 0,
            "min": min(memory_values) if memory_values else 0
        },
        "error_rate": {
            "avg": sum(error_values) / len(error_values) if error_values else 0,
            "max": max(error_values) if error_values else 0,
            "min": min(error_values) if error_values else 0
        }
    }
    
    return jsonify({
        "service": service,
        "hours": hours,
        "aggregated_metrics": aggregated,
        "sample_count": len(recent_data)
    })

if __name__ == '__main__':
    print(f"Starting Metrics Collector on port 8502 (simulation: {SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=8502, debug=True)