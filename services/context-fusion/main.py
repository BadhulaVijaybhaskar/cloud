from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import logging

app = FastAPI(title="Context Fusion Engine", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ContextSignal(BaseModel):
    source: str
    entity_id: str
    context_data: Dict[str, Any]
    timestamp: str
    tenant_id: str

class FusedContext(BaseModel):
    entity_id: str
    unified_context: Dict[str, Any]
    sources: List[str]
    fusion_hash: str
    tenant_id: str

# Mock context store
context_store = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "simulation_mode": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "fusion_operations": len(context_store),
        "simulation_mode": SIMULATION_MODE,
        "uptime_seconds": 3600
    }

@app.post("/fusion/ingest")
async def ingest_signal(signal: ContextSignal):
    """Ingest context signal from various sources"""
    try:
        if SIMULATION_MODE:
            # Mock fusion logic
            entity_key = f"{signal.tenant_id}:{signal.entity_id}"
            
            if entity_key not in context_store:
                context_store[entity_key] = {
                    "sources": [],
                    "context": {},
                    "last_updated": datetime.utcnow().isoformat()
                }
            
            # Merge context data
            context_store[entity_key]["sources"].append(signal.source)
            context_store[entity_key]["context"].update(signal.context_data)
            context_store[entity_key]["last_updated"] = signal.timestamp
            
            # Generate fusion hash
            context_str = json.dumps(context_store[entity_key]["context"], sort_keys=True)
            fusion_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
            
            logger.info(f"Fused context for {entity_key} from {signal.source}")
            
            return {
                "status": "fused",
                "entity_id": signal.entity_id,
                "fusion_hash": fusion_hash,
                "sources_count": len(set(context_store[entity_key]["sources"]))
            }
        else:
            # Real implementation would connect to Graph Core, Neural Fabric, etc.
            raise HTTPException(status_code=503, detail="External services unavailable")
            
    except Exception as e:
        logger.error(f"Fusion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fusion/context/{entity_id}")
async def get_fused_context(entity_id: str, tenant_id: str):
    """Retrieve fused context for entity"""
    entity_key = f"{tenant_id}:{entity_id}"
    
    if entity_key not in context_store:
        raise HTTPException(status_code=404, detail="Context not found")
    
    context_data = context_store[entity_key]
    context_str = json.dumps(context_data["context"], sort_keys=True)
    fusion_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    return FusedContext(
        entity_id=entity_id,
        unified_context=context_data["context"],
        sources=list(set(context_data["sources"])),
        fusion_hash=fusion_hash,
        tenant_id=tenant_id
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9101)