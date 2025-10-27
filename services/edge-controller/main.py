from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Edge Controller", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class RouteRequest(BaseModel):
    user_location: str
    service: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "edge-controller", "simulation": SIMULATION_MODE}

@app.post("/route")
def route_request(request: RouteRequest):
    """Route request to optimal region"""
    if SIMULATION_MODE:
        region_map = {
            "US": "us-east-1",
            "EU": "eu-west-1", 
            "ASIA": "ap-south-1"
        }
        
        region = region_map.get(request.user_location, "us-east-1")
        return {
            "target_region": region,
            "endpoint": f"https://{region}.atom.cloud/{request.service}",
            "latency_ms": 45
        }
    
    return {"error": "Routing unavailable"}

@app.get("/failover/status")
def failover_status():
    """Get failover status"""
    if SIMULATION_MODE:
        return {
            "primary_region": "us-east-1",
            "backup_regions": ["eu-west-1", "ap-south-1"],
            "failover_ready": True
        }
    
    return {"error": "Failover unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8403)