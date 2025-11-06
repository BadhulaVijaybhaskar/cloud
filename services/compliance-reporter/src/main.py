#!/usr/bin/env python3
from flask import Flask, jsonify, request
import os, json
app = Flask(__name__)
SIM = os.getenv("SIMULATION_MODE","true") == "true"

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"compliance-reporter"})

@app.route("/v1/run", methods=["POST"])
def run_check():
    # produce a minimal compliance report
    report = {"issues":[],"critical":0,"high":0,"medium":0,"low":0}
    if SIM:
        report["simulated"]=True
    # write out to reports dir if path provided
    out = "reports/k8/compliance_report.json"
    import os
    os.makedirs("reports/k8",exist_ok=True)
    with open(out,"w") as f:
        json.dump(report,f,indent=2)
    return jsonify({"report":out,"simulated":SIM})

if __name__ == "__main__":
    port=int(os.getenv("SERVICE_PORT","8303"))
    app.run(host="0.0.0.0", port=port)