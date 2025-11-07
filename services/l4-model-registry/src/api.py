from flask import Flask, request, jsonify
import os, time

app = Flask(__name__)
MODELS = []

@app.route('/health')
def health():
    return jsonify({"status":"healthy","service":"l4-model-registry"})

@app.route('/v1/models', methods=['POST'])
def register_model():
    data = request.json or {}
    entry = {
        "model_id": data.get("model_id", f"model-{int(time.time())}"),
        "version": data.get("version", "1.0.0"),
        "checksum": data.get("checksum", "sha256:abc123"),
        "registered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    MODELS.append(entry)
    return jsonify(entry), 201

@app.route('/v1/models')
def list_models():
    return jsonify(MODELS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('SERVICE_PORT', 9110)))