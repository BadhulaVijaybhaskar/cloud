#!/usr/bin/env python3
from flask import Flask, jsonify, request
import os

PORT = int(os.getenv("PORT", "9006"))
SIM = os.getenv("SIMULATION_MODE", "true").lower() == "true"
app = Flask("l3-gateway")

@app.route("/health")
def health():
    return jsonify({"status":"healthy","role":"l3-gateway","simulation":SIM})

@app.route("/metrics")
def metrics():
    return "# HELP l3_gateway_requests_total Total requests\nl3_gateway_requests_total 0\n", 200, {'Content-Type': 'text/plain'}

@app.route("/v1/proxy", methods=["POST"])
def proxy():
    body = request.get_json() or {}
    return jsonify({"proxied": True, "simulation": SIM, "received": body}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)