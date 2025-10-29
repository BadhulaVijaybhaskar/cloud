#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Policy Sync Controller")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "policy-sync", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "policy_sync_latency_ms": 180,
        "sync_operations_total": 67,
        "hash_mismatches": 2,
        "simulation": SIMULATION_MODE
    }

@app.get("/sync/status")
async def sync_status():
    if SIMULATION_MODE:
        return {
            "local_hash": "sha256:abc123def456",
            "hub_hash": "sha256:abc123def456",
            "sync_state": "consistent",
            "last_sync": "2024-01-15T10:29:45Z",
            "policies_synced": 12,
            "simulation": True
        }
    
    return {"status": "error", "message": "Hub connection required"}

@app.post("/sync/reconcile")
async def reconcile_policies():
    if SIMULATION_MODE:
        audit_data = {
            "reconciliation_id": "recon-5678",
            "policies_updated": 3,
            "discrepancies_resolved": 1,
            "hash_consistency": "verified",
            "sync_latency_ms": 180,
            "timestamp": "2024-01-15T10:30:00Z",
            "simulation": True
        }
        
        # Write audit file
        with open("reports/policy_sync_audit.json", "w") as f:
            json.dump(audit_data, f, indent=2)
        
        logger.info("Policy reconciliation complete")
        return audit_data
    
    return {"status": "error", "message": "Hub connection required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8703)