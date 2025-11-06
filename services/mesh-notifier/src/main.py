#!/usr/bin/env python3
"""
Mesh Notifier - Event-driven alerts for policy, billing, and delegation
"""
import os, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9004"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class NotifierHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "mesh-notifier"})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/notify":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            notification = {
                "id": f"notif-{int(time.time())}",
                "type": payload.get("type", "policy_alert"),
                "sent": True,
                "simulation": SIM
            }
            self._send(200, notification)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), NotifierHandler)
    print(f"Mesh Notifier listening on {PORT} (SIM={SIM})")
    server.serve_forever()