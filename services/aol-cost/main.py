#!/usr/bin/env python3
import os,json
from flask import Flask,request,jsonify

app = Flask(__name__)
SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.route("/health")
def health():
    return {"status": "ok", "service": "aol-cost", "simulation_mode": SIM_MODE}

@app.route("/estimate", methods=["POST"])
def estimate():
    data = request.get_json()
    rec_id = data.get("recommendation_id", "unknown")
    
    cost = {"current": 100.0, "projected": 85.0, "savings": 15.0, "currency": "USD"}
    
    return jsonify({"recommendation_id": rec_id, "cost_estimate": cost})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9305)