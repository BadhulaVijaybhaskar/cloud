#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os, uuid

app = Flask(__name__)
SIM = os.getenv("SIMULATION_MODE","true") == "true"

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"billing-gateway"})

@app.route("/v1/billing/event", methods=["POST"])
def billing_event():
    body = request.get_json() or {}
    event_id = str(uuid.uuid4())
    # Basic schema validation minimal
    required = ["tenant_id","workspace_id","resource","usage","unit","price_usd","timestamp"]
    missing=[k for k in required if k not in body]
    if missing:
        return jsonify({"error":"missing_fields","missing":missing}),400
    # In sim, accept and echo
    if SIM:
        return jsonify({"event_id":event_id,"status":"accepted","simulated":True}),202
    # Live forwarding logic would go here...
    return jsonify({"event_id":event_id,"status":"accepted","simulated":False}),202

@app.route("/v1/billing/events/<eid>", methods=["GET"])
def event_status(eid):
    return jsonify({"event_id":eid,"status":"processed","simulated":SIM})

if __name__ == "__main__":
    port=int(os.getenv("SERVICE_PORT", "8300"))
    app.run(host="0.0.0.0", port=port)