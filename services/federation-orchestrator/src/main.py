#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8900))
HEARTBEAT_SEC = int(os.getenv('HEARTBEAT_SEC', 30))

# In-memory storage for simulation
nodes_registry = {}
proposals = {}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/register-node', methods=['POST'])
def register_node():
    """Register a federation node with metadata and opt-in status"""
    data = request.get_json() or {}
    
    node_id = data.get('node_id', str(uuid.uuid4()))
    node_metadata = {
        "id": node_id,
        "region": data.get('region', 'unknown'),
        "endpoint": data.get('endpoint', 'localhost'),
        "opt_in_status": data.get('opt_in_status', False),
        "registered_at": datetime.utcnow().isoformat() + "Z",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE
    }
    
    nodes_registry[node_id] = node_metadata
    
    # Store registration for audit
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/node_registration_{node_id}.json", 'w') as f:
        json.dump(node_metadata, f, indent=2)
    
    return jsonify({"node_id": node_id, "status": "registered"})

@app.route('/v1/nodes')
def list_nodes():
    """List all registered nodes and their health status"""
    return jsonify({
        "nodes": list(nodes_registry.values()),
        "total_count": len(nodes_registry),
        "opted_in_count": sum(1 for n in nodes_registry.values() if n.get('opt_in_status'))
    })

@app.route('/v1/propose-action', methods=['POST'])
def propose_action():
    """Propose a cross-region federated action"""
    data = request.get_json() or {}
    
    proposal_id = str(uuid.uuid4())
    proposal = {
        "id": proposal_id,
        "action_type": data.get('action_type', 'metadata_sync'),
        "source_node": data.get('source_node'),
        "target_nodes": data.get('target_nodes', []),
        "payload": data.get('payload', {}),
        "status": "pending_validation",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE
    }
    
    proposals[proposal_id] = proposal
    
    # Store proposal for audit
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/proposal_{proposal_id}.json", 'w') as f:
        json.dump(proposal, f, indent=2)
    
    return jsonify({"proposal_id": proposal_id, "status": "submitted"})

@app.route('/v1/proposals/<proposal_id>')
def get_proposal(proposal_id):
    """Get proposal status and artifacts"""
    if proposal_id not in proposals:
        return jsonify({"error": "Proposal not found"}), 404
    
    return jsonify(proposals[proposal_id])

@app.route('/v1/proposals')
def list_proposals():
    """List all proposals"""
    return jsonify({
        "proposals": list(proposals.values()),
        "count": len(proposals)
    })

if __name__ == '__main__':
    print(f"Starting Federation Orchestrator on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)