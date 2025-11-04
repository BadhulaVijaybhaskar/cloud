#!/usr/bin/env python3
"""
ATOM Marketplace Gateway
API Gateway for marketplace services with routing and auth
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from datetime import datetime

app = FastAPI(title="ATOM Marketplace Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# Service endpoints
MARKETPLACE_CORE_URL = os.getenv('MARKETPLACE_CORE_URL', 'http://localhost:8100')
MODEL_REGISTRY_URL = os.getenv('MODEL_REGISTRY_URL', 'http://localhost:8101') 
AGENT_REGISTRY_URL = os.getenv('AGENT_REGISTRY_URL', 'http://localhost:8102')

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "marketplace-gateway",
        "simulation_mode": SIMULATION_MODE,
        "upstreams": {
            "marketplace_core": MARKETPLACE_CORE_URL,
            "model_registry": MODEL_REGISTRY_URL,
            "agent_registry": AGENT_REGISTRY_URL
        }
    }

@app.api_route("/api/v1/publish/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_publish(request: Request, path: str):
    """Proxy to marketplace-core for publish operations"""
    
    url = f"{MARKETPLACE_CORE_URL}/v1/{path}"
    
    if SIMULATION_MODE:
        # Simulate response
        if request.method == "POST" and "model" in path:
            return {
                "job_id": "sim-job-123",
                "status": "accepted",
                "simulation_mode": True
            }
        return {"simulation_mode": True, "proxied_to": url}
    
    # Real proxy logic would go here
    return {"proxied_to": url, "method": request.method}

@app.api_route("/api/v1/models/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_models(request: Request, path: str):
    """Proxy to model-registry"""
    
    url = f"{MODEL_REGISTRY_URL}/v1/models/{path}"
    
    if SIMULATION_MODE:
        if request.method == "GET":
            return {
                "models": [],
                "total": 0,
                "simulation_mode": True
            }
        return {"simulation_mode": True, "proxied_to": url}
    
    return {"proxied_to": url, "method": request.method}

@app.api_route("/api/v1/agents/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_agents(request: Request, path: str):
    """Proxy to agent-registry"""
    
    url = f"{AGENT_REGISTRY_URL}/v1/agents/{path}"
    
    if SIMULATION_MODE:
        if request.method == "GET":
            return {
                "agents": [],
                "total": 0,
                "simulation_mode": True
            }
        return {"simulation_mode": True, "proxied_to": url}
    
    return {"proxied_to": url, "method": request.method}

@app.get("/api/v1/marketplace/stats")
async def marketplace_stats():
    """Aggregate marketplace statistics"""
    
    if SIMULATION_MODE:
        return {
            "total_models": 42,
            "total_agents": 15,
            "total_downloads": 1337,
            "active_vendors": 8,
            "simulation_mode": True
        }
    
    # Real aggregation would query all services
    return {"simulation_mode": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8103)