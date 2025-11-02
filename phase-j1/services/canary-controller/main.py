#!/usr/bin/env python3
"""
J.1.2 Live Canary Controller - Production canary deployments
"""

from fastapi import FastAPI, Request, HTTPException
import os, json, time, uuid, logging, random

app = FastAPI(title="Live Canary Controller", version="1.0.0")
logger = logging.getLogger("canary-controller")
logging.basicConfig(level=logging.INFO)

# Global state
canaries = {}
simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "canary-controller",
        "simulation_mode": simulation_mode,
        "active_canaries": len([c for c in canaries.values() if c["status"] == "running"])
    }

@app.get("/metrics")
async def metrics():
    return {
        "canaries_total": len(canaries),
        "active_canaries": sum(1 for c in canaries.values() if c["status"] == "running"),
        "successful_canaries": sum(1 for c in canaries.values() if c["status"] == "promoted"),
        "failed_canaries": sum(1 for c in canaries.values() if c["status"] == "rolled_back")
    }

@app.post("/v1/canary/start")
async def start_canary(request: Request):
    """Start canary deployment"""
    body = await request.json()
    
    canary_id = str(uuid.uuid4())
    service_name = body.get("service_name", "unknown")
    traffic_percentage = body.get("traffic_percentage", 10)
    
    # P17: Deployment Verification
    if not body.get("smoke_tests_passed"):
        raise HTTPException(status_code=400, detail="P17 violation: Smoke tests must pass before canary")
    
    canary = {
        "id": canary_id,
        "service_name": service_name,
        "traffic_percentage": traffic_percentage,
        "status": "running",
        "started_at": time.time(),
        "metrics": {
            "success_rate": 0.0,
            "latency_p95": 0.0,
            "error_rate": 0.0
        },
        "simulation_mode": simulation_mode
    }
    
    canaries[canary_id] = canary
    logger.info(f"Started canary {canary_id} for {service_name} with {traffic_percentage}% traffic")
    
    return {
        "canary_id": canary_id,
        "status": "running",
        "service_name": service_name,
        "traffic_percentage": traffic_percentage
    }

@app.get("/v1/canary/{canary_id}")
async def get_canary(canary_id: str):
    """Get canary status and metrics"""
    if canary_id not in canaries:
        raise HTTPException(status_code=404, detail="Canary not found")
    
    canary = canaries[canary_id]
    
    # Simulate live metrics collection
    if simulation_mode and canary["status"] == "running":
        canary["metrics"] = {
            "success_rate": round(random.uniform(0.95, 0.99), 3),
            "latency_p95": round(random.uniform(100, 300), 1),
            "error_rate": round(random.uniform(0.001, 0.01), 4)
        }
    
    return canary

@app.post("/v1/canary/{canary_id}/promote")
async def promote_canary(canary_id: str):
    """Promote canary to full production"""
    if canary_id not in canaries:
        raise HTTPException(status_code=404, detail="Canary not found")
    
    canary = canaries[canary_id]
    
    # Check metrics before promotion
    metrics = canary["metrics"]
    if metrics["success_rate"] < 0.95 or metrics["error_rate"] > 0.05:
        raise HTTPException(status_code=400, detail="Canary metrics do not meet promotion criteria")
    
    canary["status"] = "promoted"
    canary["promoted_at"] = time.time()
    canary["traffic_percentage"] = 100
    
    logger.info(f"Promoted canary {canary_id} to full production")
    
    return {
        "canary_id": canary_id,
        "status": "promoted",
        "promoted_at": canary["promoted_at"]
    }

@app.post("/v1/canary/{canary_id}/rollback")
async def rollback_canary(canary_id: str):
    """Rollback canary deployment"""
    if canary_id not in canaries:
        raise HTTPException(status_code=404, detail="Canary not found")
    
    canary = canaries[canary_id]
    
    # P18: Rollback Readiness
    canary["status"] = "rolled_back"
    canary["rolled_back_at"] = time.time()
    canary["traffic_percentage"] = 0
    
    logger.warning(f"Rolled back canary {canary_id}")
    
    return {
        "canary_id": canary_id,
        "status": "rolled_back",
        "rolled_back_at": canary["rolled_back_at"]
    }

@app.get("/v1/canaries")
async def list_canaries():
    """List all canaries"""
    return {
        "canaries": list(canaries.values()),
        "total": len(canaries)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10002)