#!/usr/bin/env python3
"""
Delegation Service - Cross-tenant token delegation & approval workflows
"""
import os, json, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9001"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class DelegationHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "delegation-service"})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/delegate":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            token = f"del-{str(uuid.uuid4())[:8]}" if SIM else "LIVE_TOKEN"
            result = {"delegation_token": token, "tenant": payload.get("tenant", "default"), "simulation": SIM}
            self._send(201, result)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), DelegationHandler)
    print(f"Delegation Service listening on {PORT} (SIM={SIM})")
    server.serve_forever()