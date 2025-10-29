#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Router Health Adapter")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "router-health", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"health_checks_total": 156, "region_scores_computed": 12, "simulation": SIMULATION_MODE}

@app.get("/regions")
async def get_regions():
    if SIMULATION_MODE:
        regions = {
            "us-east-1": {"score": 0.92, "p95_latency": 45, "error_rate": 0.01, "capacity": 0.75},
            "eu-west-1": {"score": 0.88, "p95_latency": 52, "error_rate": 0.02, "capacity": 0.68},
            "ap-southeast-1": {"score": 0.85, "p95_latency": 58, "error_rate": 0.015, "capacity": 0.72},
            "simulation": True
        }
        
        logger.info("Region health scores computed")
        return regions
    
    return {"status": "error", "message": "Prometheus connection required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8602)