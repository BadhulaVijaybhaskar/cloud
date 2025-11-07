from flask import Flask, jsonify, request
import os
import json
from datetime import datetime
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l6-audit-store"})

@app.route("/v1/audit", methods=["POST"])
def audit():
    data = request.json or {}
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": data.get("event_type", "unknown"),
        "source": data.get("source", "l6-system"),
        "details": data.get("details", {}),
        "simulated": sim
    }
    
    return jsonify({
        "audit_id":"audit-001",
        "status":"stored",
        "entry":audit_entry
    })

@app.route("/v1/audit/<audit_id>")
def get_audit(audit_id):
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({
        "audit_id":audit_id,
        "event_type":"policy_evaluation",
        "timestamp":"2024-01-01T00:00:00Z",
        "simulated":sim
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9204)))