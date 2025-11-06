#!/usr/bin/env python3
"""
Ledger Service - Immutable billing + compliance ledger
"""
import os, json, time, hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", "9002"))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"
LEDGER_PATH = os.getenv("LEDGER_PATH", "reports/l2/ledger.json")

class LedgerHandler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "healthy", "service": "ledger-service"})
        elif self.path == "/v1/ledger":
            ledger = self.load_ledger()
            self._send(200, {"entries": len(ledger), "simulation": SIM})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/v1/record":
            length = int(self.headers.get('content-length', 0))
            payload = json.loads(self.rfile.read(length).decode() or "{}")
            entry_id = self.record_entry(payload)
            self._send(201, {"entry_id": entry_id, "simulation": SIM})
        else:
            self._send(404, {"error": "not_found"})

    def load_ledger(self):
        os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
        if os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH) as f:
                return json.load(f)
        return []

    def record_entry(self, data):
        ledger = self.load_ledger()
        entry = {
            "id": hashlib.md5(json.dumps(data).encode()).hexdigest()[:8],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data": data,
            "simulation": SIM
        }
        ledger.append(entry)
        with open(LEDGER_PATH, "w") as f:
            json.dump(ledger, f, indent=2)
        return entry["id"]

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), LedgerHandler)
    print(f"Ledger Service listening on {PORT} (SIM={SIM})")
    server.serve_forever()