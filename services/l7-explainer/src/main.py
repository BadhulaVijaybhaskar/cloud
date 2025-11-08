from flask import Flask, jsonify, request
app = Flask(__name__)
@app.route('/health')
def health(): return jsonify(status='healthy')
@app.route('/v1/explain', methods=['POST'])
def explain():
    payload = request.get_json() or {}
    return jsonify(id='ex-1', explanation='simulated explanation', payload=payload), 201
if __name__=='__main__':
    app.run(host='0.0.0.0', port=9203)
