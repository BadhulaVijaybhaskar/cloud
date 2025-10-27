from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict

app = FastAPI(title="ATOM Region Registry", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class RegionInfo(BaseModel):
    name: str
    url: str
    status: str = "active"
    public_key: str = ""

# In-memory registry for simulation
regions_db = {
    "us-east-1": {"name": "us-east-1", "url": "https://us-east-1.atom.cloud", "status": "active", "registered_at": "2024-01-15T10:00:00"},
    "eu-west-1": {"name": "eu-west-1", "url": "https://eu-west-1.atom.cloud", "status": "active", "registered_at": "2024-01-15T10:00:00"}
}

def enforce_p2_policy(operation: str, region_name: str):
    """P2: Region operations must be signed and audited"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "region_hash": hashlib.sha256(region_name.encode()).hexdigest()[:16],
        "service": "region-registry",
        "policy": "P2"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "region-registry", "simulation": SIMULATION_MODE}

@app.post("/region/register")
def register_region(region: RegionInfo):
    """Register new region with P2 enforcement"""
    enforce_p2_policy("register", region.name)
    
    if SIMULATION_MODE:
        regions_db[region.name] = {
            "name": region.name,
            "url": region.url,
            "status": region.status,
            "registered_at": datetime.now().isoformat()
        }
        return {"message": "Region registered (simulation)", "region": region.name}
    
    # Real implementation would validate cosign signature
    raise HTTPException(status_code=503, detail="Registry unavailable")

@app.get("/region/list")
def list_regions():
    """List all registered regions"""
    if SIMULATION_MODE:
        return {"regions": list(regions_db.values()), "total": len(regions_db)}
    
    raise HTTPException(status_code=503, detail="Registry unavailable")

@app.get("/region/{region_name}")
def get_region(region_name: str):
    """Get specific region info"""
    if SIMULATION_MODE:
        if region_name in regions_db:
            return regions_db[region_name]
        raise HTTPException(status_code=404, detail="Region not found")
    
    raise HTTPException(status_code=503, detail="Registry unavailable")

@app.get("/metrics")
def metrics():
    return {"regions_total": len(regions_db), "active_regions": 2, "simulation_mode": SIMULATION_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8401)