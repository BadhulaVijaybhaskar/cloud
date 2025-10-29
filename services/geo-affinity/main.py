#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI, Query

app = FastAPI(title="GeoIP & Affinity Module")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "geo-affinity", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"geoip_lookups_total": 234, "affinity_calculations": 89, "simulation": SIMULATION_MODE}

@app.get("/affinity")
async def get_affinity(ip: str = Query(...)):
    if SIMULATION_MODE:
        # Mock GeoIP lookup
        geo_map = {
            "1.2.3.4": {"country": "US", "region": "us-east-1", "lat": 40.7128, "lon": -74.0060},
            "5.6.7.8": {"country": "DE", "region": "eu-west-1", "lat": 52.5200, "lon": 13.4050},
            "9.10.11.12": {"country": "SG", "region": "ap-southeast-1", "lat": 1.3521, "lon": 103.8198}
        }
        
        geo = geo_map.get(ip, {"country": "US", "region": "us-east-1", "lat": 40.7128, "lon": -74.0060})
        
        result = {
            "client_ip": ip,
            "geo": geo,
            "nearest_regions": [
                {"region": geo["region"], "estimated_rtt_ms": 15},
                {"region": "us-west-2", "estimated_rtt_ms": 85},
                {"region": "eu-central-1", "estimated_rtt_ms": 120}
            ],
            "simulation": True
        }
        
        logger.info(f"GeoIP lookup: {ip} -> {geo['region']}")
        return result
    
    return {"status": "error", "message": "GeoIP database required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8603)