from flask import Flask, jsonify, request
app = Flask(__name__)
@app.route("/health")
def health(): return jsonify(status="healthy")
@app.route("/v1/proposals", methods=["POST"])
def create_proposal():
    data = request.get_json() or {}
    return jsonify(id="prop-sim-1", status="created", payload=data), 201
@app.route("/v1/proposals/<pid>", methods=["GET"])
def get_proposal(pid):
    return jsonify(id=pid, status="created")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9200)
