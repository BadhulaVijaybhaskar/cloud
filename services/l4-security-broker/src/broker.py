from flask import Flask, request, jsonify
import os
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status":"healthy"})

@app.route('/v1/token', methods=['POST'])
def token():
    # Issue a short-lived token (simulated)
    return jsonify({"token":"simulated-token","ttl":300})

@app.route('/v1/validate', methods=['POST'])
def validate():
    return jsonify({"valid":True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9130)))