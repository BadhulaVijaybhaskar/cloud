from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Federation Sync", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class SyncRequest(BaseModel):
    source_region: str
    target_region: str
    table: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "federation-sync", "simulation": SIMULATION_MODE}

@app.post("/sync/replicate")
def replicate_data(request: SyncRequest):
    """Replicate data between regions"""
    if SIMULATION_MODE:
        return {
            "sync_id": f"sync_{request.source_region}_{request.target_region}",
            "status": "completed",
            "rows_synced": 150,
            "completed_at": datetime.now().isoformat()
        }
    
    return {"error": "Replication unavailable"}

@app.get("/sync/status")
def sync_status():
    """Get replication status"""
    if SIMULATION_MODE:
        return {
            "active_syncs": 2,
            "last_sync": "2024-01-15T10:00:00",
            "regions": ["us-east-1", "eu-west-1"]
        }
    
    return {"error": "Sync unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8402)