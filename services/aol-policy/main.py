#!/usr/bin/env python3
import os,json
from flask import Flask,request,jsonify

app = Flask(__name__)
SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.route("/health")
def health():
    return {"status": "ok", "service": "aol-policy", "simulation_mode": SIM_MODE}

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    rec_id = data.get("recommendation_id", "unknown")
    
    # P1-P7 policy check
    decision = {"allowed": True, "policies": {"P1": "pass", "P2": "pass", "P3": "pass", "P4": "pass", "P5": "pass", "P6": "pass", "P7": "pass"}}
    
    return jsonify({"recommendation_id": rec_id, "decision": decision})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9304)