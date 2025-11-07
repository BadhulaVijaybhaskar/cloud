from flask import Flask, request, jsonify
import os, time, uuid

app = Flask(__name__)
SIM = os.getenv('SIMULATION_MODE', 'true') == 'true'

@app.route('/health')
def health():
    return jsonify({"status":"healthy","service":"l4-orchestrator","simulation":SIM})

@app.route('/v1/proposals', methods=['POST'])
def proposals():
    data = request.json or {}
    proposal_id = str(uuid.uuid4())[:8]
    return jsonify({"proposal_id":proposal_id,"status":"accepted","simulation":SIM}), 202

@app.route('/v1/jobs', methods=['POST'])
def jobs():
    data = request.json or {}
    job_id = f"job-{int(time.time())}"
    return jsonify({"job_id":job_id,"status":"queued","simulation":SIM}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9100)))