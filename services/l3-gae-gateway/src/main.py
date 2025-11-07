#!/usr/bin/env python3
"""
L3 GAE Gateway - Cross-region API gateway with mTLS
"""
import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9006"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class GatewayHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "l3-gae-gateway"})
        elif self.path == "/openapi.json":
            spec = {"openapi": "3.0.0", "info": {"title": "L3 GAE API", "version": "1.0.0"}}
            self._send(200, spec)
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/artifacts":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            result = {"artifact_id": payload.get("id", "art-sim"), "accepted": True, "simulation": SIM}
            self._send(201, result)
        elif self.path == "/v1/proposals":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            result = {"proposal_id": f"prop-{hash(str(payload)) % 10000}", "status": "pending", "simulation": SIM}
            self._send(201, result)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), GatewayHandler)
    print(f"L3 GAE Gateway listening on {PORT} (SIM={SIM})")
    server.serve_forever()