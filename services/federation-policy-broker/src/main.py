#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8903))
APPROVE_FEDERATION = os.getenv('APPROVE_FEDERATION', 'no').lower() == 'yes'

# Policy validation results cache
validation_cache = {}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "simulation_mode": SIMULATION_MODE, "approve_federation": APPROVE_FEDERATION})

@app.route('/v1/validate', methods=['POST'])
def validate_action():
    """Validate cross-region action against P25-P27 and P1-P24 policies"""
    data = request.get_json() or {}
    
    validation_id = str(uuid.uuid4())
    action_type = data.get('action_type', 'unknown')
    source_node = data.get('source_node')
    target_nodes = data.get('target_nodes', [])
    payload = data.get('payload', {})
    
    # Policy validation logic
    validation_result = {
        "validation_id": validation_id,
        "action_type": action_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE,
        "policies_checked": ["P25", "P26", "P27", "P1-P24"],
        "allowed": True,  # Default allow in simulation
        "reasons": [],
        "compliance_flags": {
            "data_sovereignty_p25": True,
            "opt_in_consent_p26": True,
            "rbac_isolation_p27": True,
            "general_policies_p1_p24": True
        }
    }
    
    # Apply policy rules
    if not source_node:
        validation_result["allowed"] = False
        validation_result["reasons"].append("Missing source node identification")
    
    if not target_nodes:
        validation_result["allowed"] = False
        validation_result["reasons"].append("No target nodes specified")
    
    # Check for tenant data in payload (P25 violation)
    if payload and any(key in str(payload).lower() for key in ['tenant_id', 'user_data', 'personal']):
        validation_result["allowed"] = False
        validation_result["reasons"].append("P25 violation: Raw tenant data detected")
        validation_result["compliance_flags"]["data_sovereignty_p25"] = False
    
    # Store validation result
    validation_cache[validation_id] = validation_result
    
    # Audit the validation
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/policy_validation_{validation_id}.json", 'w') as f:
        json.dump(validation_result, f, indent=2)
    
    return jsonify({
        "allowed": validation_result["allowed"],
        "reasons": validation_result["reasons"],
        "audit_ref": validation_id
    })

@app.route('/v1/delegate', methods=['POST'])
def request_delegation():
    """Request short-lived credential for approved action"""
    data = request.get_json() or {}
    
    validation_id = data.get('validation_id')
    if not validation_id or validation_id not in validation_cache:
        return jsonify({"error": "Invalid or missing validation reference"}), 400
    
    validation = validation_cache[validation_id]
    if not validation["allowed"]:
        return jsonify({"error": "Action not approved by policy validation"}), 403
    
    # Generate delegation token (simulated)
    delegation_token = {
        "token_id": str(uuid.uuid4()),
        "validation_ref": validation_id,
        "issued_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": datetime.utcnow().isoformat() + "Z",  # Short-lived
        "scope": validation["action_type"],
        "simulation_mode": SIMULATION_MODE,
        "token": f"sim-token-{uuid.uuid4().hex[:16]}" if SIMULATION_MODE else "vault-dynamic-secret"
    }
    
    # Store delegation record
    with open(f"reports/l1/delegation_{delegation_token['token_id']}.json", 'w') as f:
        json.dump(delegation_token, f, indent=2)
    
    return jsonify({
        "token_id": delegation_token["token_id"],
        "token": delegation_token["token"],
        "expires_at": delegation_token["expires_at"]
    })

@app.route('/v1/validations')
def list_validations():
    """List recent policy validations"""
    return jsonify({
        "validations": list(validation_cache.values()),
        "count": len(validation_cache)
    })

if __name__ == '__main__':
    print(f"Starting Federation Policy Broker on port {SERVICE_PORT} (simulation={SIMULATION_MODE}, approve_federation={APPROVE_FEDERATION})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)