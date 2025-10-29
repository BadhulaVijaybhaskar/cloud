#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Registry Mirror Manager")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
LOCAL_REGISTRY_URL = os.getenv("LOCAL_REGISTRY_URL", "localhost:5000")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "registry-mirror", "simulation": SIMULATION_MODE}

@app.post("/sync")
async def sync_images():
    if SIMULATION_MODE:
        mirror_state = {
            "images": [
                {"name": "atom/auth-service", "digest": "sha256:abc123", "synced": True},
                {"name": "atom/data-api", "digest": "sha256:def456", "synced": True},
                {"name": "atom/realtime", "digest": "sha256:ghi789", "synced": True}
            ],
            "registry": LOCAL_REGISTRY_URL,
            "last_sync": "2024-01-15T10:30:00Z",
            "simulation": True
        }
        
        with open("mirror_state.json", "w") as f:
            json.dump(mirror_state, f, indent=2)
        
        logger.info("Simulated registry sync complete")
        return {"status": "success", "synced": len(mirror_state["images"])}
    
    return {"status": "error", "message": "Real registry required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8602)