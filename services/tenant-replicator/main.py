from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Tenant Replicator", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class TenantSync(BaseModel):
    tenant_id: str
    target_regions: list

@app.get("/health")
def health():
    return {"status": "healthy", "service": "tenant-replicator", "simulation": SIMULATION_MODE}

@app.post("/tenant/replicate")
def replicate_tenant(request: TenantSync):
    """Replicate tenant data across regions"""
    if SIMULATION_MODE:
        return {
            "tenant_id": request.tenant_id,
            "replicated_to": request.target_regions,
            "status": "completed",
            "data_size_mb": 25.6
        }
    
    return {"error": "Tenant replication unavailable"}

@app.get("/tenant/{tenant_id}/status")
def tenant_status(tenant_id: str):
    """Get tenant replication status"""
    if SIMULATION_MODE:
        return {
            "tenant_id": tenant_id,
            "regions": ["us-east-1", "eu-west-1"],
            "last_sync": "2024-01-15T10:00:00",
            "consistency": "eventual"
        }
    
    return {"error": "Status unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8404)