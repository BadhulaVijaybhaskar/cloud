#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
SIM_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'm1-ix-bus', 'simulation': SIM_MODE}

@app.route('/v1/publish', methods=['POST'])
def publish():
    data = request.get_json()
    if SIM_MODE:
        return {'published': True, 'envelope_id': f"env_{int(time.time())}", 'simulation': True}
    return {'error': 'Production mode not implemented'}, 501

@app.route('/v1/subscribe')
def subscribe():
    if SIM_MODE:
        return {'subscribed': True, 'simulation': True, 'messages': []}
    return {'error': 'Production mode not implemented'}, 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9210)))