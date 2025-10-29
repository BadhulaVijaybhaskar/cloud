#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List

app = FastAPI(title="Event Ingestor")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class Event(BaseModel):
    tenant_id: str
    event_type: str
    severity: str = "info"
    metadata: Dict[str, Any] = {}
    timestamp: str = None

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "event-ingestor", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"events_ingested_total": 1247, "high_severity_events": 23, "simulation": SIMULATION_MODE}

@app.post("/ingest")
async def ingest_event(event: Event):
    if SIMULATION_MODE:
        # Simulate event processing
        event_id = f"evt-{hash(event.tenant_id + event.event_type) % 10000}"
        
        result = {
            "event_id": event_id,
            "status": "ingested",
            "tenant_id": event.tenant_id,
            "risk_score": 0.3 if event.severity == "high" else 0.1,
            "forwarded_to": "risk-analyzer",
            "simulation": True
        }
        
        logger.info(f"Event ingested: {event_id} for tenant {event.tenant_id}")
        return result
    
    return {"status": "error", "message": "Event processing infrastructure required"}

@app.get("/events/{tenant_id}")
async def get_events(tenant_id: str):
    if SIMULATION_MODE:
        return {
            "tenant_id": tenant_id,
            "events": [
                {"id": "evt-1234", "type": "resource_spike", "severity": "medium"},
                {"id": "evt-5678", "type": "auth_failure", "severity": "high"}
            ],
            "total": 2,
            "simulation": True
        }
    
    return {"status": "error", "message": "Event storage required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8801)