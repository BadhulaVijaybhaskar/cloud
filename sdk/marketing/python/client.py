#!/usr/bin/env python3
import requests
import os

BASE_URL = os.getenv("K9_MARKETING_URL", "http://localhost:8808")

class MarketingClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    def create_campaign(self, name, budget, region="US"):
        payload = {"name": name, "budget": budget, "region": region}
        r = requests.post(f"{self.base_url}/v1/campaigns", json=payload)
        return r.json()
    def simulate(self, proposal_id):
        return {"proposal_id": proposal_id, "simulated": True}

if __name__ == "__main__":
    client = MarketingClient()
    print(client.create_campaign("demo", 5000))