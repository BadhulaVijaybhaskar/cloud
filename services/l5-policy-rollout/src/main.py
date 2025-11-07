# services/l5-policy-rollout/src/main.py
from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l5-policy-rollout"})

@app.route("/v1/policy/deploy", methods=["POST"])
def deploy_policy():
    body = request.json or {}
    approve = os.getenv("APPROVE_L5_DEPLOY", "no")
    if approve != "yes":
        return jsonify({"error":"P36 violation: APPROVE_L5_DEPLOY required"}), 403
    
    if os.getenv("SIMULATION_MODE", "true") == "true":
        return jsonify({"policy_id":"sim-pol-001","status":"deployed","simulated":True})
    return jsonify({"policy_id":"pol-001","status":"deploying"})

@app.route("/v1/policy/<policy_id>/rollback", methods=["POST"])
def rollback_policy(policy_id):
    return jsonify({"policy_id":policy_id,"status":"rolled_back"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9203)))