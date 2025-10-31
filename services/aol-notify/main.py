#!/usr/bin/env python3
import os,json
from flask import Flask,request,jsonify

app = Flask(__name__)
SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.route("/health")
def health():
    return {"status": "ok", "service": "aol-notify", "simulation_mode": SIM_MODE}

@app.route("/notify", methods=["POST"])
def notify():
    data = request.get_json()
    rec_id = data.get("recommendation_id", "unknown")
    
    if SIM_MODE:
        result = {"status": "simulated", "sent": False}
    else:
        result = {"status": "sent", "sent": True}
    
    return jsonify({"recommendation_id": rec_id, "notification": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9306)