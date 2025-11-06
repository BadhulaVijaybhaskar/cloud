#!/usr/bin/env python3
import os, json, random
from flask import Flask, request, jsonify

app = Flask(__name__)
SIM = os.getenv("SIMULATION_MODE","true") == "true"

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"k9-agent-core"})

@app.route("/v1/propose", methods=["POST"])
def propose():
    payload = request.get_json() or {}
    pid = "prop-"+str(abs(hash(json.dumps(payload)))%1000000)
    if SIM:
        # simulate proposal + simulation
        return jsonify({"proposal_id": pid, "simulated": True}), 201
    return jsonify({"proposal_id": pid, "simulated": False}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",8808)))