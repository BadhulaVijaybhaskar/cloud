#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, time

PORT = int(os.getenv("PORT", "9005"))
SIM = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status":"healthy","role":"l3-orchestrator","simulation":SIM})
        elif self.path == "/metrics":
            metrics = "# HELP l3_proposals_total Total proposals\nl3_proposals_total 0\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(metrics.encode())
        else:
            self._send(404, {"error":"not found"})

    def do_POST(self):
        if self.path == "/v1/propose":
            length = int(self.headers.get('content-length',0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            proposal_id = f"prop-{int(time.time())}"
            result = {"proposal_id": proposal_id, "accepted": SIM, "simulation": SIM}
            self._send(202, result)
        else:
            self._send(404, {"error":"not found"})

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"l3-orchestrator running on :{PORT} (SIM={SIM})")
    server.serve_forever()