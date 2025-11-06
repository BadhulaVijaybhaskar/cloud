#!/usr/bin/env python3
from flask import Flask, jsonify, request
import os, random, json

app = Flask(__name__)
SIM = os.getenv("SIMULATION_MODE","true") == "true"

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"finops-engine"})

@app.route("/v1/forecast", methods=["POST"])
def forecast():
    # minimal forecast stub
    payload = request.get_json() or {}
    sample = {"forecast_usd": round(random.uniform(10.0,100.0),2)}
    if SIM:
        sample["simulated"]=True
    return jsonify(sample)

@app.route("/v1/allocations")
def allocations():
    return jsonify({"allocations":[{"tenant":"tenantA","cost":123.45}]})

if __name__ == "__main__":
    port=int(os.getenv("SERVICE_PORT","8302"))
    app.run(host="0.0.0.0", port=port)