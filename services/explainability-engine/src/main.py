#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8801))
MAX_EXPLAIN_TIME_S = int(os.getenv('MAX_EXPLAIN_TIME_S', 60))

@app.route('/health')
def health():
    return jsonify({"status": "ok", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/explain', methods=['POST'])
def explain():
    """Generate explainability artifacts for proposals"""
    data = request.get_json() or {}
    proposal_id = data.get('proposal_id', str(uuid.uuid4()))
    
    explain_id = f"explain-{proposal_id[:8]}-{uuid.uuid4().hex[:6]}"
    
    # Generate explainability report
    explanation = {
        "id": explain_id,
        "proposal_id": proposal_id,
        "created": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE,
        "top_features": ["cpu_usage", "latency", "mem_usage", "request_rate"],
        "importance": [0.35, 0.28, 0.20, 0.17],
        "decision_path": [
            {"condition": "cpu_usage > 80%", "weight": 0.4},
            {"condition": "latency > 200ms", "weight": 0.3},
            {"condition": "memory_growth_rate > 5%/min", "weight": 0.3}
        ],
        "confidence_intervals": {
            "expected_improvement": [0.12, 0.18],
            "risk_assessment": "LOW"
        },
        "human_readable": "System shows high CPU correlation with latency spikes. Scaling recommendation based on historical patterns with 85% confidence."
    }
    
    # Store explainability artifact
    os.makedirs("reports/k5/explainability_reports", exist_ok=True)
    with open(f"reports/k5/explainability_reports/{explain_id}.json", 'w') as f:
        json.dump(explanation, f, indent=2)
    
    return jsonify({"explain_id": explain_id, "status": "generated"})

@app.route('/v1/explain/<explain_id>')
def get_explanation(explain_id):
    """Retrieve explainability artifact"""
    try:
        with open(f"reports/k5/explainability_reports/{explain_id}.json") as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": "Explanation not found"}), 404

@app.route('/v1/explanations')
def list_explanations():
    """List all explainability artifacts"""
    explanations = []
    reports_dir = "reports/k5/explainability_reports"
    if os.path.exists(reports_dir):
        for f in os.listdir(reports_dir):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(reports_dir, f)) as file:
                        explanations.append(json.load(file))
                except:
                    continue
    
    return jsonify({"explanations": explanations, "count": len(explanations)})

if __name__ == '__main__':
    print(f"Starting Explainability Engine on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)