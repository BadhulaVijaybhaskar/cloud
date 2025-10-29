from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

app = FastAPI(title="Temporal Context Tracker", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
CONTEXT_REFRESH_INTERVAL_MS = int(os.getenv("CONTEXT_REFRESH_INTERVAL_MS", "5000"))

class ContextSnapshot(BaseModel):
    entity_id: str
    context_state: Dict[str, Any]
    timestamp: str
    snapshot_hash: str
    tenant_id: str

class ContextDrift(BaseModel):
    entity_id: str
    drift_score: float
    changed_keys: List[str]
    trend: str
    tenant_id: str

# Mock temporal store
temporal_store = {}
drift_analytics = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "simulation_mode": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "tracked_entities": len(temporal_store),
        "drift_calculations": len(drift_analytics),
        "simulation_mode": SIMULATION_MODE,
        "refresh_interval_ms": CONTEXT_REFRESH_INTERVAL_MS
    }

@app.post("/temporal/snapshot")
async def create_snapshot(snapshot: ContextSnapshot):
    """Store time-windowed context snapshot"""
    try:
        entity_key = f"{snapshot.tenant_id}:{snapshot.entity_id}"
        
        if entity_key not in temporal_store:
            temporal_store[entity_key] = []
        
        # Verify snapshot hash
        context_str = json.dumps(snapshot.context_state, sort_keys=True)
        expected_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
        
        if snapshot.snapshot_hash != expected_hash:
            raise HTTPException(status_code=400, detail="Snapshot hash mismatch")
        
        # Store snapshot with timestamp
        temporal_store[entity_key].append({
            "context_state": snapshot.context_state,
            "timestamp": snapshot.timestamp,
            "hash": snapshot.snapshot_hash
        })
        
        # Keep only last 100 snapshots per entity
        if len(temporal_store[entity_key]) > 100:
            temporal_store[entity_key] = temporal_store[entity_key][-100:]
        
        logger.info(f"Stored snapshot for {entity_key}")
        
        return {
            "status": "stored",
            "entity_id": snapshot.entity_id,
            "snapshot_count": len(temporal_store[entity_key])
        }
        
    except Exception as e:
        logger.error(f"Snapshot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temporal/drift/{entity_id}")
async def calculate_drift(entity_id: str, tenant_id: str, window_minutes: int = 60):
    """Compute context drift and trend analytics"""
    entity_key = f"{tenant_id}:{entity_id}"
    
    if entity_key not in temporal_store or len(temporal_store[entity_key]) < 2:
        raise HTTPException(status_code=404, detail="Insufficient snapshots for drift calculation")
    
    snapshots = temporal_store[entity_key]
    cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
    
    # Filter snapshots within time window
    recent_snapshots = [
        s for s in snapshots 
        if datetime.fromisoformat(s["timestamp"].replace('Z', '+00:00')) > cutoff_time
    ]
    
    if len(recent_snapshots) < 2:
        return ContextDrift(
            entity_id=entity_id,
            drift_score=0.0,
            changed_keys=[],
            trend="stable",
            tenant_id=tenant_id
        )
    
    # Calculate drift between first and last snapshot in window
    first_context = recent_snapshots[0]["context_state"]
    last_context = recent_snapshots[-1]["context_state"]
    
    # Simple drift calculation
    all_keys = set(first_context.keys()) | set(last_context.keys())
    changed_keys = []
    
    for key in all_keys:
        if first_context.get(key) != last_context.get(key):
            changed_keys.append(key)
    
    drift_score = len(changed_keys) / max(len(all_keys), 1)
    
    # Determine trend
    if drift_score > 0.5:
        trend = "volatile"
    elif drift_score > 0.2:
        trend = "evolving"
    else:
        trend = "stable"
    
    drift_result = ContextDrift(
        entity_id=entity_id,
        drift_score=drift_score,
        changed_keys=changed_keys,
        trend=trend,
        tenant_id=tenant_id
    )
    
    # Cache drift analytics
    drift_analytics[entity_key] = drift_result.dict()
    
    return drift_result

@app.get("/temporal/history/{entity_id}")
async def get_history(entity_id: str, tenant_id: str, limit: int = 10):
    """Retrieve temporal context history"""
    entity_key = f"{tenant_id}:{entity_id}"
    
    if entity_key not in temporal_store:
        raise HTTPException(status_code=404, detail="No history found")
    
    snapshots = temporal_store[entity_key][-limit:]
    
    return {
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "snapshots": snapshots,
        "total_count": len(temporal_store[entity_key])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9102)