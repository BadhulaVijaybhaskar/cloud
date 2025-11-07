#!/usr/bin/env python3
"""
L3 GAE Exchange Bus - Message routing between regions
"""
import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9008"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class BusHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "l3-gae-bus"})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/route":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            result = {"routed": True, "target": payload.get("target", "sim-node"), "simulation": SIM}
            self._send(200, result)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), BusHandler)
    print(f"L3 GAE Exchange Bus listening on {PORT} (SIM={SIM})")
    server.serve_forever()