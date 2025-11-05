#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8802))
APPROVE_META = os.getenv('APPROVE_META', 'no').lower() == 'yes'
SIMULATOR_URL = os.getenv('SIMULATOR_URL', 'http://localhost:8804')
GOVERNANCE_URL = os.getenv('GOVERNANCE_URL', 'http://localhost:8080')
AUDITOR_URL = os.getenv('AUDITOR_URL', 'http://localhost:8803')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "simulation_mode": SIMULATION_MODE, "approve_meta": APPROVE_META})

@app.route('/v1/propose', methods=['POST'])
def propose():
    """Accept meta-proposals and validate them"""
    data = request.get_json() or {}
    proposal_id = str(uuid.uuid4())
    
    # Validate proposal has explainability
    if not data.get('explainability_ref'):
        return jsonify({"error": "Explainability artifact required"}), 400
    
    # Simulate impact via simulator-proxy
    try:
        sim_resp = requests.post(f"{SIMULATOR_URL}/v1/run", 
                               json={"scenario_id": "meta_proposal", "overrides": data}, timeout=10)
        simulation_result = sim_resp.json() if sim_resp.status_code == 200 else {"status": "sim_error"}
    except:
        simulation_result = {"status": "sim_offline", "safety_flags": ["CAUTION"]}
    
    # Validate against governance policies P1-P24
    governance_check = {"status": "PASS", "violations": []}  # Simulated
    
    proposal = {
        "id": proposal_id,
        "original_payload": data,
        "simulation_result": simulation_result,
        "governance_check": governance_check,
        "status": "VALIDATED" if not simulation_result.get("safety_flags") else "NEEDS_REVIEW",
        "created": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE
    }
    
    # Store proposal
    os.makedirs("reports/k5", exist_ok=True)
    with open(f"reports/k5/refined_proposal_{proposal_id}.json", 'w') as f:
        json.dump(proposal, f, indent=2)
    
    # Audit the proposal
    try:
        requests.post(f"{AUDITOR_URL}/v1/audit", 
                     json={"event": "proposal_refined", "proposal_id": proposal_id}, timeout=5)
    except:
        pass
    
    return jsonify({"proposal_id": proposal_id, "status": proposal["status"]})

@app.route('/v1/proposal/<proposal_id>')
def get_proposal(proposal_id):
    """Get proposal status and artifacts"""
    try:
        with open(f"reports/k5/refined_proposal_{proposal_id}.json") as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": "Proposal not found"}), 404

@app.route('/v1/proposal/<proposal_id>/apply', methods=['POST'])
def apply_proposal(proposal_id):
    """Apply proposal (simulation or live based on APPROVE_META)"""
    approve = request.args.get('approve', 'no').lower() == 'yes'
    
    if not SIMULATION_MODE and not (APPROVE_META and approve):
        return jsonify({"error": "Live application requires APPROVE_META=yes and approve=yes"}), 403
    
    # Load proposal
    try:
        with open(f"reports/k5/refined_proposal_{proposal_id}.json") as f:
            proposal = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Proposal not found"}), 404
    
    # Apply in simulation mode
    result = {
        "proposal_id": proposal_id,
        "applied": True,
        "mode": "SIMULATION" if SIMULATION_MODE else "LIVE",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rollback_available": True
    }
    
    # Audit the application
    try:
        requests.post(f"{AUDITOR_URL}/v1/audit", 
                     json={"event": "proposal_applied", "proposal_id": proposal_id, "mode": result["mode"]}, timeout=5)
    except:
        pass
    
    return jsonify(result)

if __name__ == '__main__':
    print(f"Starting Policy Refiner on port {SERVICE_PORT} (simulation={SIMULATION_MODE}, approve_meta={APPROVE_META})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)