#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="QoS & Throttling Engine")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "qos-engine", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "qos_rejections_total": 12,
        "rate_limit_hits": 45,
        "circuit_breaker_trips": 2,
        "simulation": SIMULATION_MODE
    }

@app.get("/limits/{tenant_id}")
async def get_limits(tenant_id: str):
    if SIMULATION_MODE:
        limits = {
            "tenant_id": tenant_id,
            "rate_limit_rps": 1000,
            "burst_allowance": 2000,
            "quota_remaining": 85000,
            "circuit_breaker_status": "closed",
            "simulation": True
        }
        
        logger.info(f"QoS limits for tenant {tenant_id}")
        return limits
    
    return {"status": "error", "message": "Rate limiting backend required"}

@app.post("/throttle")
async def check_throttle(request: dict):
    if SIMULATION_MODE:
        tenant_id = request.get("tenant_id", "unknown")
        
        result = {
            "allowed": True,
            "tenant_id": tenant_id,
            "remaining_quota": 84999,
            "retry_after_ms": 0,
            "reason": "within_limits",
            "simulation": True
        }
        
        return result
    
    return {"status": "error", "message": "Throttling engine required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8604)