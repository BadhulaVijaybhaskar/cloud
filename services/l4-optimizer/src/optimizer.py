from flask import Flask, request, jsonify
import os
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status":"healthy"})

@app.route('/v1/optimize', methods=['POST'])
def optimize():
    payload = request.json or {}
    return jsonify({"plan_id":"plan-1","status":"simulated"}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9140)))