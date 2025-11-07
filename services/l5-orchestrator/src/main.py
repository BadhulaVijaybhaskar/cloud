# services/l5-orchestrator/src/main.py
from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l5-orchestrator"})

@app.route("/v1/rollout", methods=["POST"])
def rollout():
    body = request.json or {}
    if os.getenv("SIMULATION_MODE", "true") == "true":
        return jsonify({"id":"sim-rollout-0001","status":"scheduled","simulated":True}), 202
    return jsonify({"id":"rollout-0001","status":"started"}), 202

@app.route("/v1/rollout/<rollout_id>/status")
def rollout_status(rollout_id):
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({"id":rollout_id,"status":"running" if not sim else "simulated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9200)))