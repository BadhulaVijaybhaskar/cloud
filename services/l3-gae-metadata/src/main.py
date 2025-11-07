#!/usr/bin/env python3
"""
L3 GAE Metadata Store - Artifact metadata and policy bindings
"""
import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9007"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class MetadataHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "l3-gae-metadata"})
        elif self.path.startswith("/v1/metadata/"):
            artifact_id = self.path.split("/")[-1]
            metadata = {"artifact_id": artifact_id, "policies": ["P25", "P26"], "simulation": SIM}
            self._send(200, metadata)
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/metadata":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            result = {"stored": True, "artifact_id": payload.get("artifact_id"), "simulation": SIM}
            self._send(201, result)
        else:
            self._send(404, {"error": "not_found"})

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), MetadataHandler)
    print(f"L3 GAE Metadata Store listening on {PORT} (SIM={SIM})")
    server.serve_forever()