#!/usr/bin/env python3
"""
AI-Proxy Gateway Service - External API Gateway
Handles authentication, routing, and rate limiting for AI services
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import redis
import httpx
from datetime import datetime
import jwt

# Environment Configuration
COMPONENT_NAME = os.getenv("COMPONENT_NAME", "ai-proxy-gateway")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8081"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://langgraph-core:8080")
WORKFLOW_REGISTRY_URL = os.getenv("WORKFLOW_REGISTRY_URL", "http://workflow-registry:8084")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")

app = FastAPI(title="AI-Proxy Gateway", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if SIMULATION_MODE else ["https://*.atom-cloud.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connections
redis_client = None
http_client = None

@app.on_event("startup")
async def startup():
    global redis_client, http_client
    
    http_client = httpx.AsyncClient(timeout=30.0)
    
    if not SIMULATION_MODE:
        try:
            redis_client = redis.from_url(REDIS_URL)
        except Exception as e:
            print(f"Redis connection error: {e}")

@app.on_event("shutdown")
async def shutdown():
    if http_client:
        await http_client.aclose()

# Authentication Dependency
async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token and extract tenant information"""
    if SIMULATION_MODE:
        return {"tenant_id": "simulation-tenant", "user_id": "simulation-user"}
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": COMPONENT_NAME,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    metrics = [
        f"# HELP ai_proxy_requests_total Total API requests",
        f"# TYPE ai_proxy_requests_total counter",
        f"ai_proxy_requests_total{{service=\"{COMPONENT_NAME}\"}} 0"
    ]
    return "\n".join(metrics)

@app.post("/v1/graphs/execute")
async def execute_graph(
    request: Dict[str, Any],
    auth_data: dict = Depends(verify_token)
):
    """Proxy graph execution requests to LangGraph service"""
    if SIMULATION_MODE:
        return {
            "execution_id": f"sim_exec_{int(datetime.utcnow().timestamp())}",
            "status": "queued",
            "mode": "simulation"
        }
    
    try:
        request["tenant_id"] = auth_data["tenant_id"]
        response = await http_client.post(f"{LANGGRAPH_URL}/v1/execute", json=request)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LangGraph service error: {str(e)}")

@app.post("/v1/workflows/trigger")
async def trigger_workflow(
    request: Dict[str, Any],
    auth_data: dict = Depends(verify_token)
):
    """Proxy workflow trigger requests to Workflow Registry service"""
    if SIMULATION_MODE:
        return {
            "workflow_execution_id": f"sim_wf_{int(datetime.utcnow().timestamp())}",
            "status": "triggered",
            "mode": "simulation"
        }
    
    try:
        request["tenant_id"] = auth_data["tenant_id"]
        response = await http_client.post(f"{WORKFLOW_REGISTRY_URL}/v1/trigger", json=request)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Workflow Registry error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)