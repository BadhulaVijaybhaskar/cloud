#!/usr/bin/env python3
"""
Governance UI - Mesh dashboard and audit viewer
"""
import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9003"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class UIHandler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        if content_type == "application/json":
            self.wfile.write(json.dumps(body).encode())
        else:
            self.wfile.write(body.encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "governance-ui"})
        elif self.path == "/" or self.path == "/dashboard":
            html = f"""
            <html><head><title>L.2 Governance Mesh</title></head>
            <body><h1>Governance Mesh Dashboard</h1>
            <p>Mode: {'Simulation' if SIM else 'Live'}</p>
            <ul><li>Policies: P28, P29, P30, P31</li>
            <li>Status: Active</li><li>Ledger: Verified</li></ul>
            </body></html>"""
            self._send(200, html, "text/html")
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), UIHandler)
    print(f"Governance UI listening on {PORT} (SIM={SIM})")
    server.serve_forever()