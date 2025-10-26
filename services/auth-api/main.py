from fastapi import FastAPI, HTTPException
import jwt
import time
import os
from prometheus_client import Counter, generate_latest

app = FastAPI(title="ATOM Auth API", version="1.0.0")

# Metrics
auth_counter = Counter('auth_requests_total', 'Total auth requests', ['type'])

JWT_SECRET = os.getenv("JWT_SECRET", "atom-dev-secret")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth-api"}

@app.post("/login")
async def login(credentials: dict):
    auth_counter.labels(type="login").inc()
    
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    
    # Simulation mode accepts any credentials
    if SIMULATION_MODE or (username == "admin" and password == "password"):
        token = jwt.encode({
            "user": username,
            "tenant": "default",
            "role": "admin",
            "exp": int(time.time()) + 3600
        }, JWT_SECRET, algorithm="HS256")
        return {"token": token, "user": {"username": username, "role": "admin"}}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users")
async def get_users():
    return {"users": [
        {"id": 1, "username": "admin", "email": "admin@atom.cloud", "role": "admin"},
        {"id": 2, "username": "user", "email": "user@atom.cloud", "role": "user"}
    ]}

@app.post("/users")
async def create_user(user_data: dict):
    auth_counter.labels(type="create_user").inc()
    return {"id": 3, "username": user_data.get("username"), "created": True}

@app.post("/policies/dryrun")
async def policy_dryrun(policy_data: dict):
    return {"valid": True, "simulation": SIMULATION_MODE, "policy": policy_data}

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)