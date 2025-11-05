#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8800))
EXPERIENCE_REPO_URL = os.getenv('EXPERIENCE_REPO_URL', 'http://localhost:8701')
EXPLAINABILITY_URL = os.getenv('EXPLAINABILITY_URL', 'http://localhost:8801')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/learn', methods=['POST'])
def learn():
    """Analyze patterns and generate meta-proposals"""
    data = request.get_json() or {}
    
    # Generate proposal based on patterns
    proposal_id = str(uuid.uuid4())
    
    # Simulate learning from experience repository
    proposal = {
        "id": proposal_id,
        "type": "scaling_optimization",
        "confidence": 0.85,
        "expected_gain": "15% latency reduction",
        "created": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE,
        "source_patterns": ["high_cpu_correlation", "memory_leak_detection"],
        "rollback_id": f"rollback-{proposal_id[:8]}"
    }
    
    # Request explainability
    try:
        explain_resp = requests.post(f"{EXPLAINABILITY_URL}/v1/explain", 
                                   json={"proposal_id": proposal_id}, timeout=5)
        if explain_resp.status_code == 200:
            proposal["explainability_ref"] = explain_resp.json().get("explain_id")
    except:
        proposal["explainability_ref"] = "explain-stub-001"
    
    # Store proposal
    os.makedirs("reports/k5", exist_ok=True)
    with open(f"reports/k5/proposal_{proposal_id}.json", 'w') as f:
        json.dump(proposal, f, indent=2)
    
    return jsonify(proposal)

@app.route('/v1/proposals')
def list_proposals():
    """List all generated proposals"""
    proposals = []
    reports_dir = "reports/k5"
    if os.path.exists(reports_dir):
        for f in os.listdir(reports_dir):
            if f.startswith("proposal_") and f.endswith(".json"):
                try:
                    with open(os.path.join(reports_dir, f)) as file:
                        proposals.append(json.load(file))
                except:
                    continue
    
    return jsonify({"proposals": proposals, "count": len(proposals)})

if __name__ == '__main__':
    print(f"Starting Meta Learner on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)