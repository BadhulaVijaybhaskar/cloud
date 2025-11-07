# services/l5-edge-adapter/src/main.py
from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l5-edge-adapter"})

@app.route("/v1/edge/sync", methods=["POST"])
def sync_edge():
    body = request.json or {}
    if os.getenv("SIMULATION_MODE", "true") == "true":
        return jsonify({"sync_id":"sim-sync-001","status":"synced","simulated":True})
    return jsonify({"sync_id":"sync-001","status":"syncing"})

@app.route("/v1/edge/nodes")
def list_nodes():
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({"nodes":["edge-1","edge-2"],"simulated":sim})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9204)))