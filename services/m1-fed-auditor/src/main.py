#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
SIM_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'
audit_events = []

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'm1-fed-auditor', 'simulation': SIM_MODE}

@app.route('/v1/audit', methods=['POST'])
def audit():
    data = request.get_json()
    if SIM_MODE:
        event = {**data, 'timestamp': int(time.time()), 'id': f"audit_{len(audit_events)}"}
        audit_events.append(event)
        return {'recorded': True, 'event_id': event['id']}
    return {'error': 'Production mode not implemented'}, 501

@app.route('/v1/audit', methods=['GET'])
def get_audit():
    if SIM_MODE:
        return {'events': audit_events[-10:], 'total': len(audit_events)}
    return {'error': 'Production mode not implemented'}, 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9230)))