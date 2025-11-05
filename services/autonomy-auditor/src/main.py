#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8803))

@app.route('/health')
def health():
    return jsonify({"status": "ok", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/audit', methods=['POST'])
def audit():
    """Ingest audit events for meta-actions"""
    data = request.get_json() or {}
    
    audit_id = str(uuid.uuid4())
    audit_event = {
        "id": audit_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": data.get('event', 'unknown'),
        "proposal_id": data.get('proposal_id'),
        "mode": data.get('mode', 'SIMULATION'),
        "metadata": data.get('metadata', {}),
        "simulation_mode": SIMULATION_MODE,
        "immutable": True
    }
    
    # Store immutable audit entry
    os.makedirs("reports/k5", exist_ok=True)
    with open(f"reports/k5/audit_{audit_id}.json", 'w') as f:
        json.dump(audit_event, f, indent=2)
    
    # Also append to audit log
    with open("reports/k5/audit_log.jsonl", 'a') as f:
        f.write(json.dumps(audit_event) + '\n')
    
    return jsonify({"audit_id": audit_id, "status": "recorded"})

@app.route('/v1/audit')
def query_audit():
    """Query audit logs with filters"""
    event_filter = request.args.get('filter')
    proposal_id = request.args.get('proposal_id')
    limit = int(request.args.get('limit', 100))
    
    audits = []
    audit_log = "reports/k5/audit_log.jsonl"
    
    if os.path.exists(audit_log):
        with open(audit_log) as f:
            for line in f:
                try:
                    audit = json.loads(line.strip())
                    
                    # Apply filters
                    if event_filter and event_filter not in audit.get('event', ''):
                        continue
                    if proposal_id and audit.get('proposal_id') != proposal_id:
                        continue
                    
                    audits.append(audit)
                    
                    if len(audits) >= limit:
                        break
                except:
                    continue
    
    return jsonify({
        "audits": audits[-limit:],  # Most recent first
        "count": len(audits),
        "filters_applied": {"event": event_filter, "proposal_id": proposal_id}
    })

@app.route('/v1/audit/stats')
def audit_stats():
    """Get audit statistics"""
    stats = {
        "total_events": 0,
        "events_by_type": {},
        "simulation_vs_live": {"SIMULATION": 0, "LIVE": 0}
    }
    
    audit_log = "reports/k5/audit_log.jsonl"
    if os.path.exists(audit_log):
        with open(audit_log) as f:
            for line in f:
                try:
                    audit = json.loads(line.strip())
                    stats["total_events"] += 1
                    
                    event_type = audit.get('event', 'unknown')
                    stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
                    
                    mode = audit.get('mode', 'SIMULATION')
                    stats["simulation_vs_live"][mode] = stats["simulation_vs_live"].get(mode, 0) + 1
                except:
                    continue
    
    return jsonify(stats)

if __name__ == '__main__':
    print(f"Starting Autonomy Auditor on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)