from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l6-edge-agent"})

@app.route("/v1/metrics")
def metrics():
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({
        "node_id":"edge-001",
        "cpu_usage":45.2,
        "memory_usage":67.8,
        "network_latency":12.5,
        "simulated":sim
    })

@app.route("/v1/action", methods=["POST"])
def action():
    data = request.json or {}
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({
        "action_id":"act-001",
        "status":"executed",
        "result":"success",
        "simulated":sim
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9202)))