from flask import Flask, request, jsonify
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l6-orchestrator"})

@app.route("/v1/observe", methods=["POST"])
def observe():
    data = request.json or {}
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({"status":"accepted","simulated":sim}), 202

@app.route("/v1/propose", methods=["POST"])
def propose():
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({
        "proposal_id":"prov-sim-0001" if sim else "prov-0001",
        "actions":[{"type":"scale","target":"svc:web","params":{"replicas":3}}],
        "risk_score":0.12,
        "simulated": sim
    }), 200

@app.route("/v1/execute", methods=["POST"])
def execute():
    approve = os.getenv("APPROVE_L6_DEPLOY", "no")
    if approve != "yes":
        return jsonify({"error":"P37 violation: APPROVE_L6_DEPLOY required"}), 403
    
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({"execution_id":"exec-001","status":"started","simulated":sim})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9200)))