#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8901))

# Active tunnels registry
active_tunnels = {}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/proxy/<node_id>', methods=['POST'])
def proxy_request(node_id):
    """Forward requests to remote node through secure tunnel"""
    data = request.get_json() or {}
    
    tunnel_id = str(uuid.uuid4())
    
    # Simulate secure tunnel creation and request forwarding
    tunnel_info = {
        "tunnel_id": tunnel_id,
        "target_node": node_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "active" if not SIMULATION_MODE else "simulated",
        "encryption": "mTLS",
        "simulation_mode": SIMULATION_MODE
    }
    
    active_tunnels[tunnel_id] = tunnel_info
    
    # Simulate response from remote node
    simulated_response = {
        "tunnel_id": tunnel_id,
        "node_id": node_id,
        "response": "Request forwarded successfully",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE
    }
    
    # Store tunnel activity for audit
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/tunnel_{tunnel_id}.json", 'w') as f:
        json.dump({
            "tunnel_info": tunnel_info,
            "request_data": data,
            "response": simulated_response
        }, f, indent=2)
    
    return jsonify(simulated_response)

@app.route('/v1/tunnels')
def list_tunnels():
    """List all active tunnels"""
    return jsonify({
        "active_tunnels": list(active_tunnels.values()),
        "count": len(active_tunnels)
    })

@app.route('/v1/tunnel/<tunnel_id>/close', methods=['POST'])
def close_tunnel(tunnel_id):
    """Close an active tunnel"""
    if tunnel_id in active_tunnels:
        active_tunnels[tunnel_id]["status"] = "closed"
        active_tunnels[tunnel_id]["closed_at"] = datetime.utcnow().isoformat() + "Z"
        return jsonify({"tunnel_id": tunnel_id, "status": "closed"})
    
    return jsonify({"error": "Tunnel not found"}), 404

if __name__ == '__main__':
    print(f"Starting Federation Gateway on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)