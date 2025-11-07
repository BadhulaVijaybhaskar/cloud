#!/usr/bin/env python3
"""
L3 GAE Auditor - Cross-region exchange audit trail
"""
import os, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9009"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class AuditorHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "l3-gae-auditor"})
        elif self.path == "/v1/audit-trail":
            trail = [{"event": "exchange_simulated", "timestamp": time.time(), "simulation": SIM}]
            self._send(200, {"trail": trail})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/record":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            result = {"recorded": True, "event_id": f"evt-{int(time.time())}", "simulation": SIM}
            self._send(201, result)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), AuditorHandler)
    print(f"L3 GAE Auditor listening on {PORT} (SIM={SIM})")
    server.serve_forever()