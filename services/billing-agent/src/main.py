#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os, json, uuid

app = Flask(__name__)
SIM = os.getenv("SIMULATION_MODE","true") == "true"
STORE="data/billing_events.json"
os.makedirs("data",exist_ok=True)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"billing-agent"})

@app.route("/v1/ingest", methods=["POST"])
def ingest():
    body = request.get_json() or {}
    eid = str(uuid.uuid4())
    body['_id']=eid
    # append to local file (simulation)
    with open(STORE,"a+") as f:
        f.write(json.dumps(body) + "\n")
    return jsonify({"ingested":eid,"simulated":SIM}),202

@app.route("/v1/invoices/<month>", methods=["GET"])
def invoices(month):
    # return simple stub
    return jsonify({"month":month,"invoices":[]})

if __name__ == "__main__":
    port=int(os.getenv("SERVICE_PORT","8301"))
    app.run(host="0.0.0.0", port=port)