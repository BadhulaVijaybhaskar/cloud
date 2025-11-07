from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","component":"l6-policy-broker"})

@app.route("/v1/evaluate", methods=["POST"])
def evaluate():
    data = request.json or {}
    action_type = data.get("action_type", "unknown")
    
    # P37 & P38 policy enforcement
    if action_type in ["delete", "scale_down_critical"]:
        return jsonify({
            "decision":"deny",
            "reason":"P37 violation: high-risk action requires manual approval",
            "policy":"P37"
        })
    
    sim = os.getenv("SIMULATION_MODE", "true") == "true"
    return jsonify({
        "decision":"allow",
        "confidence":0.92,
        "ttl":300,
        "policy":"P38",
        "simulated":sim
    })

@app.route("/v1/policies")
def policies():
    return jsonify({
        "active_policies":["P37","P38"],
        "P37":"Resilience Safety - limit concurrent global actions",
        "P38":"Cross-Region Action TTL - time-boxed actions"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("SERVICE_PORT",9203)))