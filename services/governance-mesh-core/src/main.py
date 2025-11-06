#!/usr/bin/env python3
"""
Governance Mesh Core - Policy enforcement and multi-tenant orchestration
"""
import os, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9000"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class GovernanceHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "governance-mesh-core"})
        elif self.path == "/v1/policies":
            self._send(200, {"policies": ["P28", "P29", "P30", "P31"], "simulation": SIM})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/enforce":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            result = {"policy_id": payload.get("policy", "P28"), "enforced": True, "simulation": SIM}
            self._send(200, result)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), GovernanceHandler)
    print(f"Governance Mesh Core listening on {PORT} (SIM={SIM})")
    server.serve_forever()