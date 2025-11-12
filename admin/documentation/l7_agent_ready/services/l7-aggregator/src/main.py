from flask import Flask, jsonify, request
app = Flask(__name__)
@app.route('/health')
def health(): return jsonify(status='healthy')
@app.route('/v1/collect', methods=['POST'])
def collect():
    return jsonify(status='collected'), 200
@app.route('/v1/aggregate', methods=['POST'])
def aggregate():
    return jsonify(status='aggregated', meta_model='models/meta_model.pkl'), 200
if __name__=='__main__':
    app.run(host='0.0.0.0', port=9202)
