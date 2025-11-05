#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8904))

# Sync jobs registry
sync_jobs = {}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/sync', methods=['POST'])
def trigger_sync():
    """Trigger mirror sync job for approved sanitized artifacts"""
    data = request.get_json() or {}
    
    job_id = str(uuid.uuid4())
    sync_job = {
        "job_id": job_id,
        "sync_type": data.get('sync_type', 'metadata'),
        "source_node": data.get('source_node'),
        "target_nodes": data.get('target_nodes', []),
        "artifacts": data.get('artifacts', []),
        "status": "running" if not SIMULATION_MODE else "simulated",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE,
        "compliance_check": {
            "p25_no_raw_tenant_data": True,
            "sanitized_only": True,
            "approved_artifacts": True
        }
    }
    
    # Simulate sync process
    if SIMULATION_MODE:
        sync_job.update({
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "status": "completed_simulation",
            "artifacts_synced": len(sync_job["artifacts"]),
            "bytes_transferred": 0,
            "notes": "Simulation mode - no actual data transfer"
        })
    
    sync_jobs[job_id] = sync_job
    
    # Store sync job record
    os.makedirs("reports/l1", exist_ok=True)
    with open(f"reports/l1/sync_job_{job_id}.json", 'w') as f:
        json.dump(sync_job, f, indent=2)
    
    return jsonify({"job_id": job_id, "status": sync_job["status"]})

@app.route('/v1/sync-status/<job_id>')
def get_sync_status(job_id):
    """Get sync job status"""
    if job_id not in sync_jobs:
        return jsonify({"error": "Sync job not found"}), 404
    
    return jsonify(sync_jobs[job_id])

@app.route('/v1/sync-jobs')
def list_sync_jobs():
    """List all sync jobs"""
    return jsonify({
        "sync_jobs": list(sync_jobs.values()),
        "count": len(sync_jobs),
        "active_jobs": len([j for j in sync_jobs.values() if j["status"] == "running"])
    })

@app.route('/v1/cache/status')
def cache_status():
    """Get local cache status"""
    cache_info = {
        "cache_size_mb": 0,
        "cached_artifacts": 0,
        "last_cleanup": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE,
        "note": "Simulation mode - no actual cache"
    }
    
    return jsonify(cache_info)

@app.route('/v1/cache/clear', methods=['POST'])
def clear_cache():
    """Clear local mirror cache"""
    clear_result = {
        "cleared_at": datetime.utcnow().isoformat() + "Z",
        "artifacts_cleared": 0,
        "space_freed_mb": 0,
        "simulation_mode": SIMULATION_MODE
    }
    
    return jsonify(clear_result)

if __name__ == '__main__':
    print(f"Starting Federation Mirror Agent on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)