from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import jwt
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional

app = FastAPI(title="ATOM Launchpad Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
request_counter = Counter('gateway_requests_total', 'Total requests', ['method', 'endpoint'])

# Environment
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "atom-dev-secret")

# Service endpoints
SERVICES = {
    "data-api": "http://localhost:8011",
    "auth-api": "http://localhost:8012", 
    "storage-api": "http://localhost:8013",
    "runtime-deploy": "http://localhost:8014",
    "realtime-bridge": "http://localhost:8015",
    "metrics-proxy": "http://localhost:8016",
    "ai-proxy": "http://localhost:8017",
    "logs-api": "http://localhost:8018"
}

def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health():
    return {"status": "ok", "env": "SIM" if SIMULATION_MODE else "LIVE"}

@app.post("/auth/login")
async def login(credentials: dict):
    if SIMULATION_MODE:
        token = jwt.encode({"user": "admin", "tenant": "default", "exp": int(time.time()) + 3600}, JWT_SECRET)
        return {"token": token}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SERVICES['auth-api']}/login", json=credentials)
        return response.json()

@app.post("/api/data/query")
async def data_query(request: Request, query: dict):
    request_counter.labels(method="POST", endpoint="/api/data/query").inc()
    
    if SIMULATION_MODE:
        return {"rows": [[1]], "columns": ["result"]}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SERVICES['data-api']}/query", json=query)
        return response.json()

@app.get("/api/data/tables")
async def data_tables():
    if SIMULATION_MODE:
        return {"tables": ["projects", "users", "workspaces"]}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES['data-api']}/tables")
        return response.json()

@app.post("/api/ai/sql/suggest")
async def ai_suggest(context: dict):
    if SIMULATION_MODE:
        return {"suggestion": "SELECT COUNT(*) FROM users WHERE active = true", "explanation": "This query counts active users"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SERVICES['ai-proxy']}/sql/suggest", json=context)
        return response.json()

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)