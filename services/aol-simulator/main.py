#!/usr/bin/env python3
import os,json,time
from flask import Flask,request,jsonify

app = Flask(__name__)
SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.route("/health")
def health():
    return {"status": "ok", "service": "aol-simulator", "simulation_mode": SIM_MODE}

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json()
    rec_id = data.get("recommendation_id", "unknown")
    
    if SIM_MODE:
        result = {"status": "success", "simulation": True, "metrics": {"latency_p95": 450, "cpu_usage": 65}}
    else:
        time.sleep(0.1)  # Simulate work
        result = {"status": "success", "simulation": False, "metrics": {"latency_p95": 480, "cpu_usage": 62}}
    
    return jsonify({"recommendation_id": rec_id, "result": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9302)