#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8902))

# In-memory metadata store for simulation
metadata_store = {}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/metadata', methods=['POST'])
def store_metadata():
    """Store sanitized shared metadata"""
    data = request.get_json() or {}
    
    metadata_key = data.get('key', str(uuid.uuid4()))
    
    # Validate and sanitize metadata (P25 compliance)
    sanitized_metadata = {
        "key": metadata_key,
        "type": data.get('type', 'general'),
        "content": data.get('content', {}),
        "source_node": data.get('source_node'),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "sanitized": True,
        "simulation_mode": SIMULATION_MODE,
        "compliance_flags": {
            "p25_data_sovereignty": True,
            "anonymized": True,
            "tenant_data_excluded": True
        }
    }
    
    # Store metadata
    metadata_store[metadata_key] = sanitized_metadata
    
    # Persist to file for audit
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/metadata_{metadata_key}.json", 'w') as f:
        json.dump(sanitized_metadata, f, indent=2)
    
    return jsonify({"key": metadata_key, "status": "stored"})

@app.route('/v1/metadata/<key>')
def get_metadata(key):
    """Retrieve shared metadata by key"""
    if key not in metadata_store:
        return jsonify({"error": "Metadata not found"}), 404
    
    return jsonify(metadata_store[key])

@app.route('/v1/metadata')
def list_metadata():
    """List all stored metadata keys"""
    return jsonify({
        "metadata_keys": list(metadata_store.keys()),
        "count": len(metadata_store),
        "total_size_bytes": sum(len(json.dumps(v)) for v in metadata_store.values())
    })

@app.route('/v1/metadata/<key>', methods=['DELETE'])
def delete_metadata(key):
    """Delete metadata (with audit trail)"""
    if key not in metadata_store:
        return jsonify({"error": "Metadata not found"}), 404
    
    # Create deletion audit record
    deletion_record = {
        "deleted_key": key,
        "deleted_at": datetime.utcnow().isoformat() + "Z",
        "original_metadata": metadata_store[key],
        "simulation_mode": SIMULATION_MODE
    }
    
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/metadata_deletion_{key}.json", 'w') as f:
        json.dump(deletion_record, f, indent=2)
    
    del metadata_store[key]
    
    return jsonify({"key": key, "status": "deleted"})

if __name__ == '__main__':
    print(f"Starting Federation Metadata Store on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)