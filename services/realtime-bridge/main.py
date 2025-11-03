#!/usr/bin/env python3
"""
Realtime Bridge Service - Event Bus Integration
Bridges events between event bus and workflow/LangGraph services
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import redis
import httpx
from datetime import datetime
import uuid

# Environment Configuration
COMPONENT_NAME = os.getenv("COMPONENT_NAME", "realtime-bridge")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8091"))
EVENT_BUS_URL = os.getenv("EVENT_BUS_URL", "redis://localhost:6379/1")
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://langgraph-core:8080")
WORKFLOW_REGISTRY_URL = os.getenv("WORKFLOW_REGISTRY_URL", "http://workflow-registry-core:8084")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

app = FastAPI(title="Realtime Bridge", version="1.0.0")

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

class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.tenant_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, tenant_id: str = "default"):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if tenant_id not in self.tenant_connections:
            self.tenant_connections[tenant_id] = []
        self.tenant_connections[tenant_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, tenant_id: str = "default"):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if tenant_id in self.tenant_connections and websocket in self.tenant_connections[tenant_id]:
            self.tenant_connections[tenant_id].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_tenant(self, message: str, tenant_id: str):
        if tenant_id in self.tenant_connections:
            for connection in self.tenant_connections[tenant_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.disconnect(connection, tenant_id)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

class EventProcessor:
    """Event processing and routing"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.event_handlers = {}
    
    async def publish_event(self, event: Dict[str, Any]) -> str:
        """Publish event to event bus"""
        event_id = str(uuid.uuid4())
        event["id"] = event_id
        event["timestamp"] = datetime.utcnow().isoformat()
        
        if SIMULATION_MODE:
            # Simulate event publishing
            await self._simulate_event_processing(event)
        else:
            # Real Redis publishing
            if redis_client:
                await redis_client.publish("events", json.dumps(event))
        
        return event_id
    
    async def _simulate_event_processing(self, event: Dict[str, Any]):
        """Simulate event processing"""
        # Broadcast to WebSocket connections
        message = json.dumps({
            "type": "event",
            "event": event
        })
        
        tenant_id = event.get("tenant_id", "default")
        await self.connection_manager.broadcast_to_tenant(message, tenant_id)
        
        # Simulate downstream processing
        if event.get("type") == "workflow_trigger":
            await self._trigger_workflow(event)
        elif event.get("type") == "graph_execute":
            await self._execute_graph(event)
    
    async def _trigger_workflow(self, event: Dict[str, Any]):
        """Trigger workflow execution"""
        if SIMULATION_MODE:
            # Simulate workflow trigger
            response_event = {
                "type": "workflow_triggered",
                "workflow_id": event.get("workflow_id"),
                "execution_id": f"sim_wf_{int(datetime.utcnow().timestamp())}",
                "tenant_id": event.get("tenant_id"),
                "status": "queued"
            }
            
            await asyncio.sleep(1)  # Simulate processing delay
            await self.publish_event(response_event)
    
    async def _execute_graph(self, event: Dict[str, Any]):
        """Execute LangGraph"""
        if SIMULATION_MODE:
            # Simulate graph execution
            response_event = {
                "type": "graph_executed",
                "graph_id": event.get("graph_id"),
                "execution_id": f"sim_lg_{int(datetime.utcnow().timestamp())}",
                "tenant_id": event.get("tenant_id"),
                "status": "running"
            }
            
            await asyncio.sleep(2)  # Simulate processing delay
            await self.publish_event(response_event)

# Initialize managers
manager = ConnectionManager()
processor = EventProcessor(manager)

@app.on_event("startup")
async def startup():
    global redis_client, http_client
    
    http_client = httpx.AsyncClient(timeout=30.0)
    
    if not SIMULATION_MODE:
        try:
            redis_client = redis.from_url(EVENT_BUS_URL)
        except Exception as e:
            print(f"Redis connection error: {e}")

@app.on_event("shutdown")
async def shutdown():
    if http_client:
        await http_client.aclose()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": COMPONENT_NAME,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "active_connections": len(manager.active_connections),
        "tenant_connections": {k: len(v) for k, v in manager.tenant_connections.items()}
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    connection_count = len(manager.active_connections)
    metrics = [
        f"# HELP realtime_bridge_connections Active WebSocket connections",
        f"# TYPE realtime_bridge_connections gauge",
        f"realtime_bridge_connections{{service=\"{COMPONENT_NAME}\"}} {connection_count}",
        f"# HELP realtime_bridge_events_total Total events processed",
        f"# TYPE realtime_bridge_events_total counter",
        f"realtime_bridge_events_total{{service=\"{COMPONENT_NAME}\"}} 0"
    ]
    return "\n".join(metrics)

@app.post("/v1/publish")
async def publish_event(request: Dict[str, Any]):
    """Publish event to event bus"""
    try:
        event_id = await processor.publish_event(request)
        
        return {
            "event_id": event_id,
            "status": "published",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publish error: {str(e)}")

@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
    """WebSocket endpoint for real-time events"""
    await manager.connect(websocket, tenant_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connected",
                "tenant_id": tenant_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            websocket
        )
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo message back or process it
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                    websocket
                )
            else:
                # Process as event
                await processor.publish_event({**message, "tenant_id": tenant_id})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id)

@app.get("/v1/subscribe")
async def subscribe_webhook(callback_url: str, event_types: List[str] = None):
    """Register webhook for event subscription"""
    subscription_id = str(uuid.uuid4())
    
    # In a real implementation, this would store the subscription
    return {
        "subscription_id": subscription_id,
        "callback_url": callback_url,
        "event_types": event_types or ["*"],
        "status": "active"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)