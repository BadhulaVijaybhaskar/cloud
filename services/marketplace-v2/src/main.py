# services/marketplace-v2/src/main.py
import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("SERVICE_PORT", 8210))
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
        if self.path.startswith("/v1/packages"):
            # list available packages (from reports)
            try:
                import glob
                pkgs=[]
                for p in glob.glob("reports/k7/pkg-*.json"):
                    with open(p) as f:
                        pkgs.append(json.load(f))
                self._json({"packages":pkgs})
            except:
                self._json({"packages":[]})
            return
        self._json({"error":"not_found"},404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(length).decode() if length else "{}"
        payload = json.loads(body) if body else {}
        if self.path == "/v1/publish":
            job_id = "job-" + str(abs(hash(json.dumps(payload)))%100000)
            os.makedirs("reports/k7", exist_ok=True)
            with open(f"reports/k7/{job_id}.json","w") as f:
                json.dump({"job_id":job_id,"payload":payload,"status":"simulated"},f)
            self._json({"job_id":job_id,"status":"accepted"}, 202)
            return
        self._json({"error":"not_supported"},400)

def run():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Marketplace v2 running on :{PORT} (SIM={SIM})")
    server.serve_forever()

if __name__=="__main__":
    run()