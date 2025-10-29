from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Storage Sync", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class SyncRequest(BaseModel):
    source_bucket: str
    dest_bucket: str
    path: str = "/"

@app.get("/health")
def health():
    return {"status": "healthy", "service": "storage-sync", "simulation": SIMULATION_MODE}

@app.post("/storage/sync")
def sync_storage(request: SyncRequest):
    """Sync storage between clouds"""
    if SIMULATION_MODE:
        return {
            "sync_id": f"sync_{request.source_bucket}_{request.dest_bucket}",
            "status": "completed",
            "files_synced": 42,
            "bytes_transferred": 1048576
        }
    
    return {"error": "Storage sync unavailable"}

@app.get("/storage/status")
def sync_status():
    """Get storage sync status"""
    if SIMULATION_MODE:
        return {
            "active_syncs": 1,
            "completed_syncs": 15,
            "failed_syncs": 0
        }
    
    return {"error": "Sync status unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8503)