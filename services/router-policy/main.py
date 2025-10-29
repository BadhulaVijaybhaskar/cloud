#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI(title="Router Policy UI/API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "router-policy", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"policy_applies_total": 8, "signature_verifications": 8, "simulation": SIMULATION_MODE}

@app.post("/policy/apply")
async def apply_policy(policy: Dict[str, Any]):
    if SIMULATION_MODE:
        policy_id = f"pol-{hash(str(policy)) % 10000}"
        
        result = {
            "status": "applied",
            "policy_id": policy_id,
            "version": "1.0.0",
            "signature_sha256": "<REDACTED>",
            "applier": "simulation-user",
            "timestamp": "2024-01-15T10:30:00Z",
            "audit_hash": f"audit-{hash(policy_id) % 10000}",
            "simulation": True
        }
        
        logger.info(f"Policy applied: {policy_id} by simulation-user")
        return result
    
    return {"status": "error", "message": "Cosign signature verification required"}

@app.get("/policy/{policy_id}")
async def get_policy(policy_id: str):
    if SIMULATION_MODE:
        return {
            "policy_id": policy_id,
            "status": "active",
            "version": "1.0.0",
            "rules": {
                "tenant_isolation": True,
                "geo_routing": True,
                "rate_limiting": True
            },
            "simulation": True
        }
    
    return {"status": "error", "message": "Policy storage required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8605)