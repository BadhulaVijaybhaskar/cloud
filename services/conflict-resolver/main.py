from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Conflict Resolver", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ConflictData(BaseModel):
    table: str
    record_id: str
    source_value: dict
    dest_value: dict

@app.get("/health")
def health():
    return {"status": "healthy", "service": "conflict-resolver", "simulation": SIMULATION_MODE}

@app.post("/conflicts/resolve")
def resolve_conflict(conflict: ConflictData):
    """Resolve replication conflict"""
    if SIMULATION_MODE:
        # Simple last-write-wins strategy
        return {
            "resolution": "last_write_wins",
            "winner": "source",
            "resolved_value": conflict.source_value,
            "resolved_at": datetime.now().isoformat()
        }
    
    return {"error": "Conflict resolution unavailable"}

@app.get("/conflicts/pending")
def pending_conflicts():
    """Get pending conflicts"""
    if SIMULATION_MODE:
        return {
            "conflicts": [],
            "total": 0,
            "auto_resolved": 5
        }
    
    return {"error": "Conflict listing unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8504)