from flask import Flask, jsonify, request
import json, os
app = Flask(__name__)
LOG='reports/l7/audit_log.json'
@app.route('/health')
def health(): return jsonify(status='healthy')
@app.route('/v1/audit', methods=['POST'])
def audit():
    ev = request.get_json() or {}
    os.makedirs('reports/l7', exist_ok=True)
    with open(LOG,'a') as f:
        f.write(json.dumps(ev) + "\n")
    return jsonify(status='recorded'),201
if __name__=='__main__':
    app.run(host='0.0.0.0', port=9204)
