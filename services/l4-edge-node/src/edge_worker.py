from flask import Flask, request, jsonify
import os, time
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status":"healthy"})

@app.route('/v1/infer', methods=['POST'])
def infer():
    data = request.json or {}
    # simulate inference
    time.sleep(0.05)
    return jsonify({"result":"ok","simulated": os.getenv('SIMULATION_MODE','true') == 'true'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9120)))