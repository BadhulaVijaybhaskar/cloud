from fastapi import FastAPI
import os
from prometheus_client import generate_latest

app = FastAPI(title="ATOM Storage API", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "storage-api"}

@app.get("/buckets")
async def get_buckets():
    return {"buckets": ["projects", "uploads", "backups"]}

@app.post("/signed-url")
async def create_signed_url(request: dict):
    return {
        "url": f"https://storage.atom.cloud/{request.get('path', 'default')}",
        "expires": 3600,
        "simulation": True
    }

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)