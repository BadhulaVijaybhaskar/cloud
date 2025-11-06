# services/partner-portal/src/server.py
import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", 8200))
SIM = os.getenv("SIMULATION_MODE", "true") == "true"

class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_GET(self):
        if self.path == "/health":
            self._json({"status":"healthy"})
            return
        if self.path.startswith("/v1/partners"):
            # simple listing returns seeded partners in reports if in filesystem
            try:
                import glob
                partners = []
                for p in glob.glob("reports/k7/partner-test-*.json"):
                    with open(p) as f:
                        partners.append(json.load(f))
                self._json({"partners": partners})
            except Exception:
                self._json({"partners": []})
            return
        self._json({"error":"not_found"}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            payload = json.loads(body)
        except:
            payload = {}
        if self.path == "/v1/partners":
            partner_id = payload.get("name","partner")+"-sim"
            resp = {"partner_id": partner_id, "status":"created"}
            # write to reports dir for visibility (simulation)
            os.makedirs("reports/k7", exist_ok=True)
            with open(f"reports/k7/{partner_id}.json","w") as f:
                json.dump({"partner_id":partner_id,"payload":payload,"status":"pre-seeded"},f)
            self._json(resp, 201)
            return
        if self.path.endswith("/approve") and "/v1/partners/" in self.path:
            self._json({"status":"approved"})
            return
        self._json({"error":"not_supported"}, 400)

def run():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Partner Portal running on :{PORT} (SIM={SIM})")
    server.serve_forever()

if __name__ == "__main__":
    run()