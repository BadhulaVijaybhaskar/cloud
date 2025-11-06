# services/partner-sandbox/src/mock_runtime.py
import os, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", 8220))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_POST(self):
        if self.path == "/v1/run":
            length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(length).decode() if length else "{}"
            payload = json.loads(body) if body else {}
            run_id = "run-" + str(int(time.time()))
            log = {"run_id":run_id,"status":"simulated","logs":"execution simulated in sandbox"}
            os.makedirs("reports/k7", exist_ok=True)
            with open(f"reports/k7/{run_id}.json","w") as f:
                json.dump({"payload":payload,"result":log},f)
            self._json(log, 200)
            return
        self._json({"error":"not_found"},404)

    def do_GET(self):
        if self.path == "/health":
            self._json({"status":"healthy"})
            return
        self._json({"error":"not_found"},404)

def run():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Partner Sandbox running on :{PORT}")
    server.serve_forever()

if __name__=="__main__":
    run()