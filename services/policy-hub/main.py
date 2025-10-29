#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="Policy Hub Service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class PolicyManifest(BaseModel):
    name: str
    version: str
    rules: Dict[str, Any]
    signature: str = "<REDACTED>"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "policy-hub", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"policy_publish_total": 15, "signature_verifications": 15, "simulation": SIMULATION_MODE}

@app.post("/policy/publish")
async def publish_policy(policy: PolicyManifest):
    if SIMULATION_MODE:
        policy_hash = f"hash-{hash(policy.name + policy.version) % 10000}"
        
        result = {
            "status": "published",
            "policy_id": policy_hash,
            "name": policy.name,
            "version": policy.version,
            "signature_verified": True,
            "timestamp": "2024-01-15T10:30:00Z",
            "simulation": True
        }
        
        logger.info(f"Policy published: {policy.name} v{policy.version} -> {policy_hash}")
        return result
    
    return {"status": "error", "message": "Cosign verification required"}

@app.get("/policy/{policy_id}")
async def get_policy(policy_id: str):
    if SIMULATION_MODE:
        return {
            "policy_id": policy_id,
            "name": "tenant-isolation-policy",
            "version": "1.0.0",
            "status": "active",
            "rules": {
                "tenant_isolation": True,
                "namespace_enforcement": True,
                "data_anonymization": True
            },
            "signature_sha256": "<REDACTED>",
            "simulation": True
        }
    
    return {"status": "error", "message": "Policy storage required"}

@app.get("/status")
async def hub_status():
    if SIMULATION_MODE:
        return {
            "hub_status": "active",
            "policies_count": 12,
            "edge_nodes_connected": 5,
            "last_sync": "2024-01-15T10:29:45Z",
            "simulation": True
        }
    
    return {"status": "error", "message": "Hub infrastructure required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8700)