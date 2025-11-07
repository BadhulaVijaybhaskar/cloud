# services/l5-model-aggregator/src/main.py
from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l5-model-aggregator"})

@app.route("/v1/aggregate", methods=["POST"])
def aggregate():
    body = request.json or {}
    if os.getenv("SIMULATION_MODE", "true") == "true":
        return jsonify({"job_id":"sim-agg-001","status":"queued","simulated":True})
    return jsonify({"job_id":"agg-001","status":"processing"})

@app.route("/v1/models/<model_id>/federated")
def get_federated_model(model_id):
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({"model_id":model_id,"federated":True,"simulated":sim})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9201)))