#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Helm Orchestrator")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "helm-orchestrator", "simulation": SIMULATION_MODE}

@app.post("/render")
async def render_chart():
    if SIMULATION_MODE:
        helm_output = {
            "chart": "atom-chart",
            "version": "1.0.0",
            "values": {
                "replicaCount": 3,
                "image": {"repository": "atom/api", "tag": "latest"},
                "service": {"type": "ClusterIP", "port": 80}
            },
            "rendered_yaml": "# Simulated Helm output\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: atom-api\n",
            "simulation": True
        }
        
        logger.info("Simulated Helm chart render complete")
        return {"status": "success", "chart": helm_output}
    
    return {"status": "error", "message": "Real Helm required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8604)