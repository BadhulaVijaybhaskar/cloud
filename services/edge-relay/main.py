#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI, WebSocket

app = FastAPI(title="Edge Relay Service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
EDGE_NODE_ID = os.getenv("EDGE_NODE_ID", "edge-sim-001")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "edge-relay", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"relay_connections_active": 3, "messages_relayed": 89, "simulation": SIMULATION_MODE}

@app.get("/relay/status")
async def relay_status():
    if SIMULATION_MODE:
        return {
            "edge_node_id": EDGE_NODE_ID,
            "hub_connected": True,
            "mesh_peers": ["edge-002", "edge-003", "edge-004"],
            "last_heartbeat": "2024-01-15T10:30:00Z",
            "zero_trust_status": "verified",
            "simulation": True
        }
    
    return {"status": "error", "message": "Edge mesh infrastructure required"}

@app.post("/relay/sync")
async def sync_relay():
    if SIMULATION_MODE:
        sync_result = {
            "status": "synced",
            "policies_received": 8,
            "mesh_updates": 3,
            "sync_latency_ms": 150,
            "simulation": True
        }
        
        logger.info(f"Edge relay sync complete: {EDGE_NODE_ID}")
        return sync_result
    
    return {"status": "error", "message": "Hub connection required"}

@app.websocket("/ws/relay")
async def websocket_relay(websocket: WebSocket):
    await websocket.accept()
    if SIMULATION_MODE:
        await websocket.send_text(json.dumps({
            "type": "policy_update",
            "policy_id": "pol-1234",
            "action": "apply",
            "simulation": True
        }))
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8701)