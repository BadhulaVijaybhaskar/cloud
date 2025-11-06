import os, requests
class AtomPartnerClient:
    def __init__(self, base=None, token=None):
        self.base = base or os.getenv("ATOM_PARTNER_BASE", "http://localhost:8200")
        self.token = token
    def register_partner(self, payload):
        r = requests.post(f"{self.base}/v1/partners", json=payload, timeout=5)
        return r.json()