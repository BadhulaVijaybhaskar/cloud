from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Federation Policy", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class TrustRequest(BaseModel):
    region: str
    public_key: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "federation-policy", "simulation": SIMULATION_MODE}

@app.post("/trust/establish")
def establish_trust(request: TrustRequest):
    """Establish trust with new region"""
    if SIMULATION_MODE:
        return {
            "region": request.region,
            "trust_established": True,
            "expires_at": "2025-01-15T10:00:00"
        }
    
    return {"error": "Trust establishment unavailable"}

@app.get("/trust/status")
def trust_status():
    """Get federation trust status"""
    if SIMULATION_MODE:
        return {
            "trusted_regions": ["us-east-1", "eu-west-1"],
            "pending_trust": [],
            "trust_level": "high"
        }
    
    return {"error": "Trust status unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8406)