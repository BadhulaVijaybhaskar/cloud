#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
import random

app = Flask(__name__)
SIM_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'm1-cdp-bridge', 'simulation': SIM_MODE}

@app.route('/v1/translate-policy', methods=['POST'])
def translate_policy():
    data = request.get_json()
    if SIM_MODE:
        return {
            'translated_policy': data.get('policy', {}),
            'compatibility_score': round(random.uniform(0.7, 0.95), 2),
            'simulation': True
        }
    return {'error': 'Production mode not implemented'}, 501

@app.route('/v1/validate-action', methods=['POST'])
def validate_action():
    if SIM_MODE:
        return {'valid': True, 'reason': 'simulation_mode', 'policy_match': True}
    return {'error': 'Production mode not implemented'}, 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9220)))