from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Disaster Recovery", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class RecoveryRequest(BaseModel):
    region: str
    backup_id: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "disaster-recovery", "simulation": SIMULATION_MODE}

@app.post("/recovery/initiate")
def initiate_recovery(request: RecoveryRequest):
    """Initiate disaster recovery"""
    if SIMULATION_MODE:
        return {
            "recovery_id": f"recovery_{request.region}_{datetime.now().strftime('%Y%m%d')}",
            "status": "in_progress",
            "estimated_completion": "2024-01-15T12:00:00"
        }
    
    return {"error": "Recovery unavailable"}

@app.get("/recovery/validate")
def validate_backups():
    """Validate backup integrity"""
    if SIMULATION_MODE:
        return {
            "backups_validated": 5,
            "integrity_check": "passed",
            "last_validation": "2024-01-15T09:00:00"
        }
    
    return {"error": "Validation unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8405)