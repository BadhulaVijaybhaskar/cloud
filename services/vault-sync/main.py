#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Vault Sync Daemon")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
VAULT_PRIMARY_ADDR = os.getenv("VAULT_PRIMARY_ADDR", "http://vault-primary:8200")
VAULT_SECONDARY_ADDR = os.getenv("VAULT_SECONDARY_ADDR", "http://vault-secondary:8200")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "vault-sync", "simulation": SIMULATION_MODE}

@app.post("/replicate")
async def replicate_secrets():
    if SIMULATION_MODE:
        sync_log = {
            "primary": VAULT_PRIMARY_ADDR,
            "secondary": VAULT_SECONDARY_ADDR,
            "secrets_synced": [
                {"path": "secret/tenant-1/db", "status": "SYNC_SIMULATED"},
                {"path": "secret/tenant-2/api", "status": "SYNC_SIMULATED"}
            ],
            "timestamp": "2024-01-15T10:30:00Z",
            "simulation": True
        }
        
        with open("vault_sync.log", "w") as f:
            json.dump(sync_log, f, indent=2)
        
        logger.info("Simulated vault sync complete")
        return {"status": "success", "synced": len(sync_log["secrets_synced"])}
    
    return {"status": "error", "message": "Real Vault required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8603)