#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Node Join Gateway")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "node-join", "simulation": SIMULATION_MODE}

@app.post("/join")
async def join_node():
    if SIMULATION_MODE:
        join_result = {
            "nodes_joined": [
                {"name": "worker-3", "ip": "192.168.1.13", "token": "<REDACTED>", "status": "joined"},
                {"name": "worker-4", "ip": "192.168.1.14", "token": "<REDACTED>", "status": "joined"}
            ],
            "cluster_size": 5,
            "simulation": True
        }
        
        logger.info("Simulated node join complete")
        return {"status": "success", "result": join_result}
    
    return {"status": "error", "message": "Real cluster required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8605)