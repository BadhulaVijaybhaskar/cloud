#!/usr/bin/env python3
import os,json
from flask import Flask,request,jsonify

app = Flask(__name__)
SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.route("/health")
def health():
    return {"status": "ok", "service": "aol-executor", "simulation_mode": SIM_MODE}

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    rec_id = data.get("recommendation_id", "unknown")
    dry_run = data.get("dry_run", True)
    
    if SIM_MODE or dry_run:
        result = {"status": "success", "executed": False, "dry_run": True}
    else:
        result = {"status": "success", "executed": True, "dry_run": False}
    
    return jsonify({"recommendation_id": rec_id, "result": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9303)