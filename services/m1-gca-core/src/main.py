#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)
SIM_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'm1-gca-core', 'simulation': SIM_MODE}

@app.route('/v1/sign', methods=['POST'])
def sign():
    data = request.get_json()
    if SIM_MODE:
        return {
            'signature': f"sim_sig_{hashlib.md5(str(data).encode()).hexdigest()[:8]}",
            'signed_at': int(time.time()),
            'key_id': 'sim_key_001'
        }
    return {'error': 'Production mode not implemented'}, 501

@app.route('/v1/verify', methods=['POST'])
def verify():
    if SIM_MODE:
        return {'valid': True, 'reason': 'simulation_mode'}
    return {'error': 'Production mode not implemented'}, 501

@app.route('/v1/keys')
def keys():
    return {'keys': [{'id': 'sim_key_001', 'type': 'simulation'}]} if SIM_MODE else {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9200)))